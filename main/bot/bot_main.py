from main.bot.lib.tools import BaseTool, extract_function_calls, run_function_calls 
from main.bot.lib.prompts import PromptTemplate, ChatHistory
from llama_cpp import Llama
from datetime import datetime
from main.bot.tools.websearch import DuckSearch
from main.bot.tools.weather import Weather
import re

fn = """{"name": "function_name", "arguments": {"arg_1": "value_1", "arg_2": value_2, ...}}"""

inst = '''[INST]You are a helpfull AI assistant name Utachi. You will now roleplay as Utachi an human. Give a short and consise response to the user. 
You will have access to the following functions. 
${functions}

To use these functions format your response like this:
<multiplefunctions>
    <functioncall> ${fn} </functioncall>
    <functioncall> ${fn} </functioncall>
    ...
</multiplefunctions>

Try to Converse and response to User by your self first.
Use function only when needed. Do not use function when you know the Correct Answer.
[/INST]
!begin

${chat_history}
<|user|>Pooh: ${human}
<|assistant|>Utachi: '''


prompts = PromptTemplate(inputVariable=["user", "message", "start", "end"], template=inst, fnTemplate=fn)

msg = []
history = ChatHistory(messages=msg)

llm = Llama(model_path="/home/pooh/code/utachi-ai2/ggml-model-Q4_K_M.gguf",
                seed=25565,
                top_k=0,
                top_p=1.28,
                repeat_penalty=1.28,
                temperature=0.15,
                # n_ctx=32768,
                n_ctx=131072,
                n_threads=8,
                n_gpu_layers=12,
                stop=["pooh:", "Utachi:","<|im_end|>", "<function_result>","<|assistant|>", "<|function_result|>", "<|function_result|>System:", " Pooh:"]
                )

class timeTool(BaseTool):
    """Use this tool to get the current time"""

    def run(self):

        return f"The current system time is {datetime.now()}"

        
tools = [timeTool, DuckSearch, Weather]

async def gen(user_input:str) -> str:
    promt = await prompts.generatePrompt(chatHistory=history, human=user_input, tools=tools)
    print(promt)
    out = llm.create_completion(promt,stop=["pooh:", "Utachi:","<|im_end|>", "Pooh:", "\n Pooh:", "<|function_result|>"], max_tokens=3200, echo=False, stream=False)
    return out['choices'][0]['text'].strip()


def regex(text:str) -> str:
    return text

def keep_xml_and_json(text : str) -> str:
    """Keep only xml and json-like formats from the text."""
    # Extract XML-like formats
    xml_matches = re.findall(r'<[^>]*>.*?</[^>]*>', text, flags=re.DOTALL)
    # Extract JSON-like formats
    json_matches = re.findall(r'{[^}]*}', text)
    # Combine extracted parts
    combined_matches = xml_matches + json_matches
    # Join the extracted parts into a single string
    result = '\n'.join(combined_matches)
    print("debug")
    print(result)
    return result

async def main(user_input:str, iteration: int = 0) -> str:
    if iteration == 3:
        return "genration iteration limit"
    out = await gen(user_input)   
    # print(out)
    try:
        functions = extract_function_calls(out)
        if functions != False:
            clean_message = keep_xml_and_json(out)
            functions = extract_function_calls(out)
            print("111111")
            print("function being callEd!")
            # history.add_message(user="", message=out, type="Tool",)
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
            # print(type(out))
            # print(out)
    except Exception as e:
        print("Error during function call2")
        print(e)
        history.add_message(user="", message=keep_xml_and_json(out), type="Tool")
        history.add_message(user="", message=f"your function calling string contain the following error \n {e}\nPlease try again.", start="<|System|>", end="<|System|>", type="System")
        await main(user_input)

    else:
        print("no function found here")
        # print(out)


    history.add_message(user="Pooh", message=user_input, type="User", start="<|user|>")
    clean_message = remove_xml_tags(out) 
    history.add_message(user="Utachi", message=clean_message, type="AI",start="<|assistant|>")

    return clean_message

def remove_xml_tags(text:str) -> str:
    """Remove xml tags and their content from the text."""
    text = re.sub('<[^>]*>.*?<[^>]*>', '', text, flags=re.DOTALL)
    # Remove JSON-like formats
    text = re.sub('{[^}]*}', '', text)
    return text

if __name__ == "__main__":
    while True:
        user_input = input("Enter a message: ")
        if user_input == "exit":
            break
        main(user_input)
