from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
model_name = "facebook/nllb-200-distilled-600M"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
# print(tokenizer.lang_code_to_id)

def translate(text: str) -> str:

    tokenizer.src_lang = "eng_Latn"
    inputs = tokenizer(text=text, return_tensors="pt")
    translated_tokens = model.generate(
        **inputs, forced_bos_token_id=tokenizer.convert_tokens_to_ids("jpn_Jpan")
    )
    message = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
    return message

if __name__ == "__main__":
    print(translate("""hi"""))