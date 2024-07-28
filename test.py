import re

def replace_prompt(text, prompt: str, replacement):
    if text.startswith(prompt):
        return text[len(prompt):]
    else:

        # Create a pattern that matches the prompt literally
        pattern = re.compile(re.escape(prompt), re.DOTALL)
        
        # Perform the replacement
        replaced_text = pattern.sub(replacement, text)
        
        return replaced_text

# Test cases
text1 = "Hello <|user|>! How are you, <|user|>?"
prompt1 = "<|user|>"
replacement1 = "Alice"

text2 = "The quick (brown) fox jumps over the lazy dog."
prompt2 = "(brown)"
replacement2 = "red"

text3 = "This is a multi-line text.\n<|user|> appears here.\nAnd here <|user|> too."
prompt3 = "<|user|>"
replacement3 = "TOKEN"

prompt4 = """[INST]You are a helpfull assistant name Utachi.[/INST]
!begin
<|user|> what day is it today
<|assistant|>"""
text4 = """[INST]You are a helpfull assistant name Utachi.[/INST]
!begin
<|user|> what day is it today
<|assistant|> I'm sorry, but as an AI language model, I don't have real-time capabilities to provide the current date. Please check your local calendar or device for that information.<|end|>"""
replacement4 = ""
# Run tests
print(replace_prompt(text1, prompt1, replacement1))
print(replace_prompt(text2, prompt2, replacement2))
print(replace_prompt(text3, prompt3, replacement3))
print(replace_prompt(text4, prompt4, replacement4))