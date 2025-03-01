import os
os.environ['CUDA_VISIBLE_DEVICES'] = "1"
os.environ['NVIDIA_VISIBLE_DEVICES'] = "1"

from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList, BitsAndBytesConfig
import torch
from typing import List
import random
from peft import PeftModel
from dataclasses import dataclass
from main.bot.ai_stop import _SentinelTokenStoppingCriteria
import re

torch.manual_seed(0)

bnb_config = BitsAndBytesConfig(
    # load_in_8bit=True,
    # llm_int8_has_fp16_weight=True,
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.float16
)

model_ = AutoModelForCausalLM.from_pretrained("/run/media/pooh/transfer/finetune-phi3-medium-agent/model3", device_map="auto", trust_remote_code=True, quantization_config=bnb_config)

# tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-medium-128k-instruct")

# model = PeftModel.from_pretrained(model_, "/run/media/pooh/transfer/finetune-phi3-medium-agent/phi3_smol_agent")
model = model_

# @dataclass
# class config:
    

# class wordStop(StoppingCriteria):
#     def __init__(self, stop_words: List[str], starting_idx: int, tokenizer):
#         super().__init__()
#         self.stop_word_ids = [tokenizer.encode(word, add_special_tokens=False) for word in stop_words]
#         self.starting_idx = starting_idx
#         self.tokenizer = tokenizer

#     def __call__(self, input_ids: torch.LongTensor, _scores: torch.FloatTensor) -> bool:
#         for sample in input_ids:
#             trimmed_sample = sample[self.starting_idx:]
#             for stop_word_ids in self.stop_word_ids:
#                 if trimmed_sample.shape[-1] < len(stop_word_ids):
#                     continue
#                 for window in trimmed_sample.unfold(dimension=0, size=len(stop_word_ids), step=1):
#                     if torch.all(torch.eq(torch.tensor(stop_word_ids).to(window.device), window)):
#                         return True
#         return False



def genrate_model(prompt: str, stoplist: list = None) -> str:
    # tokenizer.pad_token_id
    input_ids = tokenizer(prompt, return_tensors="pt").to("cuda")

    stop_token_list = []
    if stoplist != None:
        for stop_msg in stoplist:
            sentinel_token_ids_assistant = tokenizer(stop_msg, add_special_tokens=False, return_tensors="pt").to("cuda")
            stop_token_list.append(_SentinelTokenStoppingCriteria(sentinel_token_ids=sentinel_token_ids_assistant, starting_idx=input_ids.shape[-1], stop_string=stop_msg, tokenizer=tokenizer))
    stoplists = StoppingCriteriaList(stop_token_list)

    output = model.generate(**input_ids, 
                            temperature=0.01,
                            max_length=128000,
                            top_p=1.245,
                            top_k=0,
                            # seed=0,
                            # seed=random.randint(0,65535),
                            do_sample=False,
                            repetition_penalty=1.115,
                            stopping_criteria=stoplists,
                            early_stopping=True,
                            )

    full_msg = tokenizer.decode(output[0])
    completion = full_msg[len(prompt)-2:].strip()

    return completion


if __name__ == "__main__":
    inst_prompt = """[INST]You are a helpfull assistant name Utachi..You can do functioncalling.Think through this step by step! 
You will have access to the following functions:
{"name": "timeTool", "description": "Use this tool to get the current time", "parameters": {}},{"name": "DuckSearch", "description": "Use a SearchEngine to look up information on the internet.", "parameters": {'query': {'type': 'str', 'description': 'The query to search using DuckDuckGo.'}}},{"name": "Weather", "description": "Use To get the weather of a location.", "parameters": {'location': {'type': 'str', 'description': 'The location to get the weather of.'}}},
To use these functions format your response like this:
<multiplefunctions>
    <functioncall>{"name": "function_name", "arguments": {"arg_1": "value_1", "arg_2": value_2, ...}}</functioncall>
    <functioncall>{"name": "function_name", "arguments": {"arg_1": "value_1", "arg_2": value_2, ...}}</functioncall>
    ...
</multiplefunctions>
The format is like XML with JSON embeded in it.
Try to Converse and response to User by your self first.
Give a short and consise response to the user. 
Use function only when needed. Do not use function when you know the Correct Answer.
[/INST]
!begin
"""

    # torch.manual_seed(random.randint(0,65535))
    ms = ""
    msg = genrate_model(f"{inst_prompt}<|user|>hi there how are u\n<|assistant|>I'm doing great today. How about yourself?\n<|user|>\n whats the current time\n<|assistant|>\n")
    # ms += "\n" + msg + "\n"
    print(msg)
    # print(genrate_model(inst_prompt+"<|user|>\nCan you do formatted json like function calling?\n<|assistant|>"))