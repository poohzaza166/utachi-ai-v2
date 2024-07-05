from main.bot.lib.tools import BaseTool, extract_function_calls, run_function_calls 
from main.bot.lib.prompts import PromptTemplate, ChatHistory
from llama_cpp import Llama
from datetime import datetime
from main.bot.tools.websearch import DuckSearch
from main.bot.tools.weather import Weather
import re
from pydantic import Field
from main.bot.lib.utils import keep_xml_and_json, remove_xml_tags
# from main.bot.infrence_pytorch import genrate_model


fn = """{"name": "function_name", "arguments": {"arg_1": "value_1", "arg_2": value_2, ...}}"""

inst = '''[INST]You are a helpfull assistant name Utachi.You can do functioncalling. Think through this step by step!
You will have access to the following functions. 
${functions}

To use these functions format your response like this:
<multiplefunctions>
    <functioncall> ${fn} </functioncall>
    <functioncall> ${fn} </functioncall>
    ...
</multiplefunctions>

Try to Converse and response to User by your self first.
Give a short and consise response to the user. 
Use function only when needed. Do not use function when you know the Correct Answer.
[/INST]
!begin

${chat_history}
<|user|>
${human}
<|im_end|>
<|assistant|>
'''


prompts = PromptTemplate(inputVariable=["user", "message", "start", "end"], template=inst, fnTemplate=fn)

msg = []
history = ChatHistory(messages=msg)

llm = Llama(model_path="/home/pooh/code/utachi-ai2/ggml-model-Q4_K_M.gguf",
                seed=0,
                top_k=5,
                top_p=1.24,
                repeat_penalty=1.115,
                temperature=0.37,
                # n_ctx=32768,
                # n_ctx=131072,
                n_ctx=8096,
                n_threads=8,
                # n_gpu_layers=15
                n_gpu_layers=-1,
                # stop=["pooh:", "Utachi:","<|im_end|>", "<function_result>","<|assistant|>", "<|function_result|>", "<|function_result|>SYS:", " Pooh:"]
                )

class timeTool(BaseTool):
    """Use this tool to get the current time"""

    def run(self):

        return f"The current system time is {datetime.now()}"

        
tools = [timeTool, DuckSearch, Weather]

async def gen(user_input:str) -> str:
    promt = await prompts.generatePrompt(chatHistory=history, human=user_input, tools=tools)
    print(promt)
    out = llm.create_completion(promt,stop=["<|im_end|>","<|user|>", "SYS", "<|function_result|>", " Pooh: ", "\n Pooh: ", "\n Utachi:"], max_tokens=3200, echo=False, stream=False)
    print(out)
    return out['choices'][0]['text'].strip()



async def main(user_input:str, iteration: int = 0) -> str:
    if iteration == 3:
        return "genration iteration limit"
    out = await gen(user_input)   
    try:
        functions = extract_function_calls(out)
        if functions != False:
            clean_message = keep_xml_and_json(out)
            functions = extract_function_calls(clean_message)
            print("111111")
            print("function being callEd!")
            # history.add_message(user="", message=out, type="Tool",)
            results = run_function_calls(functions, tools)
            print("resuktssss")
            print(results)
            history.add_message(user="SYS", message=str(results[0]), type="Tool", start="<|function_result|>", end="<|function_result|>")  
            if results[1] == False:
                # main(user_inpu)
                print("No functions found in the completion. or something went wrong druing functioncall")
            print("user intputed")
            print(user_input)
            out = await gen(user_input)
            print("model gen 2 res")
            # print(type(out))
            # print(out)
    except Exception as e:
        print("Error during function call2")
        print(e)
        history.add_message(user="", message=keep_xml_and_json(out), type="Tool")
        history.add_message(user="", message=f"ERROR: \n {e}\nPlease try again.", start="<|System|>", end="<|System|>", type="System")
        await main(user_input)

    else:
        print("no function found here")
        # print(out)
    print("unclean message")
    print(out)
    print("______________")

    history.add_message(user="", message=user_input, type="User", start="<|user|>")
    clean_message = remove_xml_tags(out) 
    history.add_message(user="", message=clean_message, type="AI",start="<|assistant|>")

    return clean_message


if __name__ == "__main__":
    while True:
        user_input = input("Enter a message: ")
        if user_input == "exit":
            break
        main(user_input)
