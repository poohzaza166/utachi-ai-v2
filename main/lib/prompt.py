from typing import Annotated, Dict, List, Literal, Tuple, List, Optional
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader
from string import Template
from main.lib.tools import convert_base_tool_to_prompt
class ToolsObj(BaseModel):
    name: str
    description: str
    usage: str

# Define the chat message model
class ChatMessage(BaseModel):
    user: str
    start: Optional[str] = None
    end: Optional[str] = None
    msg_type: Literal["AI", "System", "User", "Tool"]
    message: str

# Define the chat history model
class ChatHistory(BaseModel):
    messages: List[ChatMessage]

    def add_message(self, user: str, message: str, type: str, end: Optional[str] = None, start: Optional[str] = None):
        self.messages.append(ChatMessage(user=user, message=message, msg_type=type, start=start, end=end))

    def get_history(self):
        return self.messages

# Define the prompt manager
class PromptTemplate:
    def __init__(self, input_variables, template, fnTemplate):
        self.input_variables = input_variables
        self.template = Template(template)
        self.fnTemplate = fnTemplate

    def generate_prompt(self, chat_history, human, tools: List[ToolsObj] = []):
        # Check if chat_history is an instance of ChatHistory
        if not isinstance(chat_history, ChatHistory):
            raise ValueError("Input should be an instance of ChatHistory")

        # Initialize an empty string to store the formatted chat history
        formatted_chat_history = ""

        if len(chat_history.get_history()) == 0 and len(tools) == 0:
            return self.template.safe_substitute(conv_hist=formatted_chat_history.strip() if formatted_chat_history else "", chat_history="", human=human, fn=self.fnTemplate, functions="" )

        # Loop through all messages in the chat history
        for message in chat_history.get_history():
            # Create a dictionary of variables to substitute into the template
            # Initialize an empty dictionary
            vars_to_substitute = {}

            # Loop through all input variables
            for var in self.input_variables:
                # Get the value of the variable from the message object
                value = getattr(message, var)

                # Add the variable and its value to the dictionary
                if value == None:
                    vars_to_substitute[var] = ""
                else:
                    vars_to_substitute[var] = value

            # Concatenate all messages into a single string
            formatted_chat_history += f"{vars_to_substitute['start']}{vars_to_substitute['user']}: {vars_to_substitute['message']}{vars_to_substitute['end']}\n"
        functions_prompt = ""
        for tool in tools:
            var = convert_base_tool_to_prompt(tool)
            functions_prompt += f"{{\"name\": \"{var['name']}\", \"description\": \"{var['description']}\", \"parameters\": {var['parameters']}}},"
        return self.template.safe_substitute(chat_history=formatted_chat_history.strip(), human=human, functions=functions_prompt.strip(), fn=self.fnTemplate)

if __name__ == "__main__":
    # Usage
    # Create a chat history
    history = ChatHistory(messages=[])

    # Add some messages to the history
    history.add_message(user="User", message="Hello, bot!", type="User")
    history.add_message(user="Bot", message="Hello, user!", type="AI")
    history.add_message(user="meme", message="Hello, user!", type="Tool")

    # Create a prompt template
    template = """inst
${chat_history}
{human}"""
    prompt_template = PromptTemplate(input_variables=["user", "message", "start", "end"], template=template)

    # Generate a prompt
    prompt = prompt_template.generate_prompt(chat_history=history, human="Pooh", )
    print(prompt)