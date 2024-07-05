from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import torch
from transformers import VitsTokenizer, VitsModel, set_seed
from typing import Any, Tuple
import scipy
from main.translation.main import translate
from voicevox import Client
from pydub import AudioSegment
from typing import List, Union
import re

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


@router.post("/en2jp_speach")
async def en2jp_tts(input_data: InputData):
    combined = AudioSegment.empty()
    for i in chunk_text(input_data.data, 10):
        text = translate(i)
        async with Client() as client:
            audio_query = await client.create_audio_query(
                text, speaker=4
            )
            audio_query.speed_scale = 1.18
            audio_chunk = await audio_query.synthesis(speaker=4)
            
            # Convert the audio_chunk to an AudioSegment
            audio_segment = AudioSegment.from_wav(io.BytesIO(audio_chunk))
            
            combined += audio_segment
    
    output = io.BytesIO()
    combined.export(output, format="wav")
    output.seek(0)
    out = convert_pcm_to_aac(output)
    return StreamingResponse(io.BytesIO(out), media_type="audio/aac")

def chunk_text(text: str, target_words: int = 30) -> List[str]:
    # Split the text into words
    words: List[str] = re.findall(r'\S+|\n', text)
    
    # If the total word count is less than or equal to the target, return the whole text
    if len(words) <= target_words:
        return [' '.join(words).strip()]
    
    # Calculate the number of chunks
    num_chunks: int = -(-len(words) // target_words)  # Ceiling division
    
    # Create chunks using list comprehension and join
    chunks: List[str] = [' '.join(words[i*target_words:(i+1)*target_words]).strip() 
                         for i in range(num_chunks)]
    
    # Remove any empty chunks
    chunks = list(filter(bool, chunks))
    
    return chunks

def convert_pcm_to_aac(pcm_data, sample_rate=24000, channels=1, sample_width=2):
    audio = AudioSegment.from_raw(
        pcm_data,
        sample_width=sample_width,
        frame_rate=sample_rate,
        channels=channels
    )
    output_io = io.BytesIO()
    audio.export(output_io, format="adts")  # ADTS is a container format for AAC
    aac_data = output_io.getvalue()
    return aac_data