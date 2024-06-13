from main.bot.lib.tools import BaseTool, extract_function_calls, run_function_calls 
from main.bot.lib.prompts import PromptTemplate, ChatHistory
from llama_cpp import Llama
from datetime import datetime
from main.bot.tools.websearch import DuckSearch


fn = """{"name": "function_name", "arguments": {"arg_1": "value_1", "arg_2": value_2, ...}}"""

inst = '''[INST]You are a helpfull AI assistant name Utachi. You will now roleplay as Utachi. You can do functioncalling. Give a short and consise response to the user. 
You will have access to the following functions. You call the function in XML format.
${functions}
To use these functions respond with:
<multiplefunctions>
    <functioncall> ${fn} </functioncall>
    <functioncall> ${fn} </functioncall>
    ...
</multiplefunctions>
Try to answer User on your own first then use functioncalling. 
[/INST]
!begin

${chat_history}
<|user|>Pooh: ${human}
<|assistant|>Utachi: '''


prompts = PromptTemplate(inputVariable=["user", "message", "start", "end"], template=inst, fnTemplate=fn)

msg = []
history = ChatHistory(messages=msg)

llm = Llama(model_path="/home/pooh/code/utachi-ai2/bleeding edge/ggml-model-Q4_K_M.gguf",
                seed=5555,
                top_k=3,
                top_p=1.25,
                repeat_penalty=1.25,
                temperature=0.80,
                # n_ctx=32768,
                n_ctx=131072,
                n_threads=8,
                n_gpu_layers=5,
                stop=["pooh:", "Utachi:","<|im_end|>", "<function_result>","<|assistant|>", "<|function_result|>", "<|function_result|>System:", " Pooh:"]
                )

class timeTool(BaseTool):
    """Use this tool to get the current time"""

    def run(self):

        return f"The current system time is {datetime.now()}"

        
tools = [timeTool, DuckSearch]

async def gen(user_input:str) -> dict:
    promt = await prompts.generatePrompt(chatHistory=history, human=user_input, tools=tools)
    print(promt)
    out = llm.create_completion(promt,stop=["pooh:", "Utachi:","<|im_end|>", "Pooh:", "\n Pooh:", "<|function_result|>"], max_tokens=3200, echo=False, stream=False)
    return out

def regex(text:str) -> str:
    return text


async def main(user_input:str) -> str:
    out = await gen(user_input)   
    print(out['choices'][0]['text'].strip())
    try:
        functions = extract_function_calls(out['choices'][0]['text'])
    except Exception as e:
        print("Error during function call1")
        print(e)
    if functions != False:
        try:
            results = run_function_calls(functions, tools)
            print("resuktssss")
            print(results)
            history.add_message(user="System", message=str(results[0]), type="Tool", start="<|function_result|>", end="<|function_result|>")  
            if results[1] == False:
                # main(user_inpu)
                print("No functions found in the completion. or something went wrong druing functioncall")
            print("user intputed")
            print(user_input)
            out = await gen(user_input)
            print("model gen 2 res")
            print(type(out))
            print(out['choices'][0]['text'].strip())
        except Exception as e:
            print("Error during function call2")
            print(e)
    else:
        print("no function found here")
        print(out['choices'][0]['text'].strip())


    history.add_message(user="Pooh", message=user_input, type="User", start="<|user|>")
    history.add_message(user="Utachi", message=out['choices'][0]['text'], type="AI",start="<|assistant|>")
    return out['choices'][0]['text'].strip()

if __name__ == "__main__":
    while True:
        user_input = input("Enter a message: ")
        if user_input == "exit":
            break
        main(user_input)
