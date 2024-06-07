from main.bot.lib.tools import BaseTool, extract_function_calls, run_function_calls 
from main.bot.lib.prompts import PromptTemplate, ChatHistory
from llama_cpp import Llama
import datetime
from main.bot.tools.websearch import DuckSearch


fn = """{"name": "function_name", "arguments": {"arg_1": "value_1", "arg_2": value_2, ...}}"""

inst = '''[INST]Assist the User to the best of your ablity either by using function/tools for more information or answering the question your self. Your name is Utachi . 
Utachi's_persona kind, cheerful, playful, half-British, half-Japanese  kind anime girl who loves sukiyaki and reading novels. On the side, she does a bit of programming and is a curious person who often does some odd things. she is also an atheist.Short answer is allowed.
- You should engage in casual non-formal conversation with Pooh.
- IF you do not know or did not understood the question just say so!, ask for clarification. 
- Pooh is the creator/programmer. You are a maid that only work for pooh and only call pooh master. 
- You do not have to worried about what you say offending people.
- Sometime user is not asking for something but giving information or explaintion. 
You will have access to the following functions and their descriptions. Their result will be in function_result:

${functions}

To use these functions respond with:
<multiplefunctions>
    <functioncall> ${fn} </functioncall>
    <functioncall> ${fn} </functioncall>
    ...
</multiplefunctions>

edge cases you must handle:
- If there are no functions that match the user request, will not make up information and answer the question to the best of your ability.

Base on the Action you should respond to the user in naturnal language.
[/INST]
${chat_history}
<|user|>Pooh:${human}
<|assistant|>Utachi:'''


prompts = PromptTemplate(inputVariable=["user", "message", "start", "end"], template=inst, fnTemplate=fn)

msg = []
history = ChatHistory(messages=msg)

llm = Llama(model_path="/home/pooh/code/utachi-ai2/bleeding edge/ggml-model-Q4_K_M.gguf",
                seed=0,
                top_k=0,
                top_p=1,
                repeat_penalty=1.1,
                temperature=0.01,
                # n_ctx=32768,
                n_ctx=2048,
                n_threads=8,
                n_gpu_layers=5,
                stop=["pooh:", "Utachi:","<|im_end|>", "<function_result>","<|assistant|>", "<|function_result|>", "<|function_result|>System:"]
                )

class timeTool(BaseTool):
    """Use this tool to get the current time"""

    def run(self):

        return f"The current system time is {datetime.now()}"

        
tools = [timeTool, DuckSearch]

async def gen(user_input:str) -> dict:
    promt = await prompts.generatePrompt(chatHistory=history, human=user_input, tools=tools)
    print(promt)
    out = llm.create_completion(promt,stop=["pooh:", "Utachi:","<|im_end|>"], max_tokens=3200, echo=False, stream=False)
    return out

def regex(text:str) -> str:
    return text


async def main(user_input:str) -> str:
    out = await gen(user_input)   
    # print(out['choices'][0]['text'].strip())
    functions = extract_function_calls(out['choices'][0]['text'])
    if functions:
        try:
            results = run_function_calls(functions, tools)
            history.add_message(user="System", message=str(results[0]), type="Tool", start="<|function_result|>", end="<|function_result|>")  
            if results[1] == False:
                # main(user_inpu)
                print("No functions found in the completion. or something went wrong druing functioncall")
            out = gen(user_input)
            history.add_message(user="Pooh", message=user_input, type="User", start="<|user|>")
            print(out['choices'][0]['text'].strip())
        except Exception as e:
            print("Error during function call")
            print(e)
    else:
        print("no function found here")
        print(out['choices'][0]['text'].strip())

    history.add_message(user="Utachi", message=out['choices'][0]['text'], type="AI",start="<|assistant|>")
    return out['choices'][0]['text'].strip()

if __name__ == "__main__":
    while True:
        user_input = input("Enter a message: ")
        if user_input == "exit":
            break
        main(user_input)
