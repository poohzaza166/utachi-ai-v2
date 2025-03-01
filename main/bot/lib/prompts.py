from typing import Annotated, Dict, List, Literal, Optional, Union
from pydantic import BaseModel
from string import Template
from main.bot.lib.models import ToolsObj, ChatMessage, ChatHistory
from main.bot.lib.tools import convert_base_tool_to_prompt

# Define the prompt manager
class PromptTemplate:
    def __init__(self, inputVariable, template, fnTemplate):
        self.inputVariable = inputVariable
        self.template = Template(template)
        self.fnTemplate = fnTemplate

    async def generatePrompt(self, chatHistory: ChatHistory, human: str, tools: List[ToolsObj]):
        # Check if chat_history is an instance of ChatHistory
        if not isinstance(chatHistory, ChatHistory):
            raise ValueError("Input should be an instance of ChatHistory")

        # Initialize an empty string to store the formatted chat history
        formattedChatHistory = ""

        if len(chatHistory.getHistory()) == 0 and len(tools) == 0:
            return self.template.safe_substitute(conv_hist=formattedChatHistory.strip() if formattedChatHistory else "", chatHistory="", human=human, fn=self.fnTemplate, functions="" )

        # Loop through all messages in the chat history
        for message in chatHistory.getHistory():
            # Create a dictionary of variables to substitute into the template
            # Initialize an empty dictionary
            vars = {}
            # Add the user, message and type to the dictionary
            for var in self.inputVariable:
                # Get the value of the variable from the message object
                value = getattr(message, var)

                # Add the variable and its value to the dictionary
                if value == None:
                    vars[var] = ""
                else:
                    vars[var] = value
            # Add the formatted message to the formatted chat history
            if vars['user'] == "":
                formattedChatHistory += f"{vars['start']}{vars['user']}\n{vars['message']}{vars['end']}\n"
            else:
                formattedChatHistory += f"{vars['start']}{vars['user']}:{vars['message']}{vars['end']}\n"
        
        functions_prompt = ""
        for tool in tools:
            var = convert_base_tool_to_prompt(tool)
            functions_prompt += f"{{\"name\": \"{var['name']}\", \"description\": \"{var['description']}\", \"parameters\": {var['parameters']}}},"
        return self.template.safe_substitute(chat_history=formattedChatHistory.strip(), human=human, functions=functions_prompt.strip(), fn=self.fnTemplate)
