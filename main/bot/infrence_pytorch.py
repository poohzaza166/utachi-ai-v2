import os
os.environ['CUDA_VISIBLE_DEVICES'] = "1"
os.environ['NVIDIA_VISIBLE_DEVICES'] = "1"

from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList, BitsAndBytesConfig
import torch
from typing import List
import random
from peft import PeftModel
from dataclasses import dataclass

qaunt_config = BitsAndBytesConfig(load_in_8bit=True)

# model_ = AutoModelForCausalLM.from_pretrained("microsoft/Phi-3-medium-128k-instruct", device_map="auto", trust_remote_code=True, quantization_config=qaunt_config)

# tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-medium-128k-instruct")

# model = PeftModel.from_pretrained(model_, "/home/pooh/code/utachi-ai2/model3")
# model = model_

# @dataclass
# class config:
    

class wordStop(StoppingCriteria):
    def __init__(self, stop_words: List[str], starting_idx: int, tokenizer):
        super().__init__()
        self.stop_word_ids = [tokenizer.encode(word, add_special_tokens=False) for word in stop_words]
        self.starting_idx = starting_idx
        self.tokenizer = tokenizer

    def __call__(self, input_ids: torch.LongTensor, _scores: torch.FloatTensor) -> bool:
        for sample in input_ids:
            trimmed_sample = sample[self.starting_idx:]
            for stop_word_ids in self.stop_word_ids:
                if trimmed_sample.shape[-1] < len(stop_word_ids):
                    continue
                for window in trimmed_sample.unfold(dimension=0, size=len(stop_word_ids), step=1):
                    if torch.all(torch.eq(torch.tensor(stop_word_ids).to(window.device), window)):
                        return True
        return False

stoplist = StoppingCriteriaList([wordStop(stop_words=["<|end|>", "pooh: "],tokenizer=tokenizer, starting_idx=0)])


def genrate_model(prompt: str,) -> str:
    # tokenizer.pad_token_id 
    input_ids = tokenizer(prompt, return_tensors="pt").to("cuda")
    output = model.generate(**input_ids, 
                            temperature=1.0,
                            max_length=32000,
                            top_p=1.12,
                            top_k=0,
                            # seed=random.randint(0,65535),
                            do_sample=True,
                            repetition_penalty=1.1,
                            stopping_criteria=stoplist)
    return tokenizer.decode(output[0])
if __name__ == "__main__":
    inst_prompt = """[INST]You are a helpfull assistant name Utachi.[/INST]\n!begin\n"""

    # torch.manual_seed(random.randint(0,65535))
    ms = ""
    msg = genrate_model("<|user|>write a long poem\n<|assistant|>")
    ms += "\n" + msg + "\n"
    print(ms)
    # print(genrate_model(inst_prompt+"<|user|>\nCan you do formatted json like function calling?\n<|assistant|>"))