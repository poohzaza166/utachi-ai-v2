from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import torch
from transformers import VitsTokenizer, VitsModel, set_seed
from typing import Any, Tuple
import scipy
tokenizer = VitsTokenizer.from_pretrained("facebook/mms-tts-eng")
model = VitsModel.from_pretrained("facebook/mms-tts-eng")

class InputData(BaseModel):
    data: str

router = APIRouter()

def generate_audio(text:str) -> Tuple[Any, int]:
    inputs = tokenizer(text=text, return_tensors="pt")

    set_seed(555)  # make deterministic

    with torch.no_grad():
        outputs = model(**inputs)

    waveform = outputs.waveform[0]
    return waveform, model.config.sampling_rate

@router.post("/text2speech")
async def text2speech(input_data: InputData):
    input_text = input_data.data
    waveform, sampling_rate = generate_audio(input_text)

    # print(type(waveform))
    # # Convert waveform to bytes
    # waveform_bytes = waveform.tobytes()
    byte_io = io.BytesIO()
    scipy.io.wavfile.write(byte_io, rate=model.config.sampling_rate, data=waveform.cpu().numpy())

    # # Create a BytesIO object from the waveform bytes
    # waveform_io = io.BytesIO(waveform_bytes)

    return StreamingResponse(byte_io, media_type="audio/wav")