from main.lib.tools import BaseTool, extract_function_calls, run_function_calls
from main.lib.prompt import PromptTemplate, ChatHistory
from llama_cpp import Llama
import json
from main.tools.ducksearch import DuckSearch
from datetime import datetime
from main.tools.weather import Weather
from transformers import pipeline
fn = """{"name": "function_name", "arguments": {"arg_1": "value_1", "arg_2": value_2, ...}}"""

inst = '''[INST]You are an AI assistant name Utachi.
You will have access to the following functions and their descriptions. Their result will be in function_result:

${functions}

To use these functions respond with:
<multiplefunctions>
    <functioncall> ${fn} <functioncall>
    <functioncall> ${fn} <functioncall>
    ...
</multiplefunctions>

edge cases you must handle:
- If there are no functions that match the user request you will not make up information and answer the question to the best of your ability.

Base on the Action you should respond to the user in naturnal language.
[/INST]
!begin
${chat_history}
<|user|>${human}<|end|>
<|assistant|>'''


prompts = PromptTemplate(input_variables=["user", "message", "start", "end"], template=inst, fnTemplate=fn)

msg = []
history = ChatHistory(messages=msg)

llm = Llama(model_path="/home/pooh/code/utachi-ai2/ggml-model-Q4_K_M.gguf",
                seed=0,
                top_k=12,
                top_p=1.12,
                repeat_penalty=1.1,
                temperature=0.25,
                # n_ctx=32768,
                n_ctx=131072,
                n_threads=8,
                # n_gpu_layers=5,
                stop=["<|user|>"]
                )

class timeTool(BaseTool):
    """Use this tool to get the current time"""

    def run(self):

        return f"The current system time is {datetime.now()}"

        

# promt = prompts.generate_prompt(chat_history=history, human="can you do function calling", tools=[HelloTool])
# print(promt)

# out = llm.create_completion(promt,stop=["pooh:", "Utachi:","<|im_end|>"], max_tokens=250, echo=False)

# print(out['choices'][0]['text'])

def translate_en_jp(text:str) -> str:
    fugu_translator = pipeline('translation', model='staka/fugumt-en-ja')
    fugu_translator('This is a cat.')

tools = [timeTool, DuckSearch]

def gen(user_input:str) -> dict:
    promt = prompts.generate_prompt(chat_history=history, human=user_input, tools=tools)
    print(promt)
    length: int = len(promt) + 250
    out = llm.create_completion(promt,stop=["pooh:", "Utachi:"], max_tokens=length, echo=False, stream=False)
    return out

def main(user_input:str):
    out = gen(user_input)   
    print(out['choices'][0]['text'].strip())
    try:
        functions = extract_function_calls(out['choices'][0]['text'])
    except Exception as e:
        print("parsing functioncall error")
        exit()
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

    history.add_message(user="Utachi", message=out['choices'][0]['text'], type="AI",start="<|assistant|>", end="<|assistant|>")

if __name__ == "__main__":
    while True:
        user_input = input("Enter a message: ")
        if user_input == "exit":
            break
        main(user_input)

# while True:
# user_input = "make a joke using function calling"
# # if user_input == "exit":
# #     break
# # history.add_message(user="Pooh", message=user_input, type="User",end="<|end_of_turn|>")
# promt = prompts.generate_prompt(chat_history=history, human=user_input, tools=[HelloTool,SongRecommendation, Joke, BookRecommendation])
# print(promt)
# out = llm.create_completion(promt,stop=["pooh:", "Utachi:","<|im_end|>"], max_tokens=250, echo=False, stream=False)

# functions = extract_function_calls(out['choices'][0]['text'])
# if functions:
#     print(functions)
#     tools = [HelloTool, SongRecommendation, Joke, BookRecommendation]
#     results = run_function_calls(functions, tools)
#     history.add_message(user="System", message=results[0], type="Tool")  
#     if results[1] == False:
#         promt = prompts.generate_prompt(chat_history=history, human=user_input, tools=[HelloTool,SongRecommendation, Joke, BookRecommendation])
#     print(promt)
#     # 

# else:
#     print(out['choices'][0]['text'].strip())

# # print(out['choices'][0]['text'])
# history.add_message(user="Utachi", message=out['choices'][0]['text'], type="AI",end="<|end_of_turn|>")
