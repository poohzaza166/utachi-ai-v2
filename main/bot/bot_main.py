from main.bot.lib.tools import BaseTool, extract_function_calls, run_function_calls, parse_function_call, parse_message_block
from main.bot.lib.prompts import PromptTemplate, ChatHistory
from llama_cpp import Llama
from main.bot.tools.websearch import DuckSearch
from main.bot.tools.weather import Weather
from main.bot.tools.time import timeTool
import re
from pydantic import Field
from main.bot.lib.utils import keep_xml_and_json, remove_xml_tags
from main.bot.lib.event import PluginManager
from main.bot.errorException import NoFunctionFoundError, MalFormAnswerContainingFunctioncall


from main.bot.infrence_pytorch import genrate_model


fn = """{"name": "function_name", "arguments": {"arg_1": "value_1", "arg_2": value_2, ...}}"""

inst = '''[INST]You are a helpfull assistant name Utachi.You can do functioncalling.
You will have access to the following functions:
${functions}
To use these functions format your response like this:
<multiplefunctions>
    <functioncall>${fn}</functioncall>
    <functioncall>${fn}</functioncall>
    ...
</multiplefunctions>

Try to Converse and response to User by your self first.
Give a short and consise response to the user. 
Use function only when needed. Do not use function when you know the Correct Answer.
[/INST]
!begin

<|user|>
hi there how are u
<|assistant|>
I'm doing great today. How about yourself?
${chat_history}
<|user|>
${human}
<|assistant|>
'''



# llm = Llama(model_path="/home/pooh/code/utachi-ai2/ggml-model-Q4_K_M.gguf",
#                 seed=0,
#                 top_k=3,
#                 top_p=1.242,
#                 repeat_penalty=1.115,
#                 temperature=0.15,
#                 # n_ctx=32768,  
#                 # n_ctx=131072,
#                 n_ctx=8096,
#                 n_threads=8,
#                 # n_gpu_layers=15
#                 # n_gpu_layers=-1,
#                 # stop=["pooh:", "Utachi:","<|im_end|>", "<function_result>","<|assistant|>", "<|function_result|>", "<|function_result|>SYS:", " Pooh:"]
#                 )
        
tools = [timeTool, DuckSearch, Weather]


class ChatBot:
    def __init__(self) -> None:
        self.prompts = PromptTemplate(inputVariable=["user", "message", "start", "end"], template=inst, fnTemplate=fn)
        self.plugin_manage = PluginManager("plugins")
        msg = []
        self.history = ChatHistory(messages=msg)
        self.plugin_manage.load_plugins()
        

    async def main(self, user_input:str, iteration: int = 0) -> str:
        self.plugin_manage.message_bus.publish("NewMessage", user_input)
        if iteration == 3:
            return "genration iteration limit"
        out = await self.gen(user_input)
        # out = out.replace("[",'')   
        try:
            functions = extract_function_calls(out)
            # functions = parse_function_call(out)
            print(functions)
            if functions != False:
                clean_message = keep_xml_and_json(out)
                # functions = parse_function_call(clean_message)
                functions = extract_function_calls(clean_message)
                self.plugin_manage.message_bus.publish("FunctionCallRun", functions)

                # history.add_message(user="", message=keep_xml_and_json(out), type="Tool",)
                results = run_function_calls(functions, tools)

                self.plugin_manage.message_bus.publish("FunctionCallResult", results)    
                self.history.add_message(user="SYS", message=str(results[0]), type="Tool", start="<|function_result|>", end="<|function_result|>")  
               
                if results[1] == False:
                    raise NoFunctionFoundError()
                
                print("user intputed")
                print(user_input)
                out = await self.gen(user_input)
                print("model gen 2 res")

        except Exception as e:
            print("Error during function call2")
            print(e)
            self.history.add_message(user="", message=keep_xml_and_json(out), type="Tool")
            self.history.add_message(user="", message=f"ERROR: \n {e}\nPlease try again.", start="<|System|>", end="<|System|>", type="System")
            await self.main(user_input)


        self.history.add_message(user="", message=user_input, type="User", start="<|user|>")
        clean_message = remove_xml_tags(out) 
        self.history.add_message(user="", message=clean_message, type="AI",start="<|assistant|>")
        if "functioncall" in clean_message:
            print("malform functioncall")
            raise MalFormAnswerContainingFunctioncall()
        self.plugin_manage.message_bus.publish("ModelOutput", clean_message)
        return clean_message

    async def gen(self, user_input:str) -> str:
        promt = await self.prompts.generatePrompt(chatHistory=self.history, human=user_input, tools=tools)
        print(promt)
        # out = llm.create_completion(promt,stop=["<|im_end|>","<|user|>", "SYS", "<|function_result|>", " Pooh: ", "\n Pooh: ", "\n Utachi:", ".\n "], max_tokens=3200, echo=False, stream=False)
        out = genrate_model(promt,stoplist=["<|im_end|>","<|user|>", "SYS", "<|function_result|>"] )
        print(out)
        # return out['choices'][0]['text'].strip()
        return out

if __name__ == "__main__":
    while True:
        user_input = input("Enter a message: ")
        if user_input == "exit":
            break
        main(user_input)
