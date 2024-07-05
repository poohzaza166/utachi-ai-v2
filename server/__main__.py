from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from pydantic import BaseModel
import argparse 
from typing import Literal
### define user input

class UserConfig(BaseModel):
    LLM_model: str 
    presision: Literal[0, 4, 8, 16]
    # LLM_model_path : str = None


def get_user_arg():
    parser = argparse.ArgumentParser(prog="this is a server for utachiLLM")
    parser.add_argument("--model", type=str, help="modelname or model path in huggingface formatt")
    parser.add_argument("--presision", type=int, )