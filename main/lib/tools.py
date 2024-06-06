from pydantic import BaseModel, Field, validator
from typing import Type, Optional
import re
import xml.etree.ElementTree as ET
import json
from pydantic import BaseModel, Field
from typing import Optional
from typing import Type
from pydantic import ValidationError


class BaseTool(BaseModel):
    # name: str
    # description: str


    def run(self, interest: str) -> str:
        """Use the tool."""
        if not interest:
            raise ValueError("Interest cannot be empty.")
        return "Recommended Book"

    async def async_run(self, interest: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("BookRecommendation does not support async")

def convert_base_tool_to_prompt(tool_class: Type[BaseTool]) -> dict:
    """Converts a BaseTool class to a prompt."""
    # Get the input schema from the tool's run method
    input_schema = tool_class.model_fields
    # print(type(input_schema))
    # Get the output schema from the tool's run method
    output_schema = tool_class.__annotations__.get('return', None)

    # Create a dictionary of input parameters with their types
    # Initialize an empty dictionary for the parameters
    parameters = {}
    # Iterate over the items in the input schema
    for k in input_schema:
        # print(type(k))
        if k!= "name" and k != "description":
            test = tool_class.model_fields.get(k)
            print(test)
            # Add the parameter to the dictionary with its type and description
            if test.is_required() == True:
                parameters[k] = {"type": str(test.annotation).replace("<class '",'').replace("'>",""), "description": test.description}


    return {
        "name": tool_class.__name__,
        "description": tool_class.__doc__,
        "run": tool_class.run,
        "parameters": parameters,
        "output_schema": str(output_schema),
    }

def extract_function_calls(completion):
    # print("DEBUG: completion")
    # print(completion)
    completion = completion.strip()
    pattern_multiple = r"(<multiplefunctions>(.*?)</multiplefunctions>)"
    pattern_single = r"(<functioncall>(.*?)</functioncall>)"

    match = re.search(pattern_multiple, completion, re.DOTALL)
    if match:
        multiplefn = match.group(1)
        root = ET.fromstring(multiplefn)
        functions = root.findall("functioncall")
        return [json.loads(fn.text) for fn in functions]

    match = re.search(pattern_single, completion, re.DOTALL)
    if match:
        singlefn = match.group(1)
        root = ET.fromstring(singlefn)
        function = root.text
        return [json.loads(function)]

    return None
    
    
def run_function_calls(functions, tools: BaseTool) -> str:
    if functions:
        for function in functions:
            for tool in tools:
                if tool.__name__ == function["name"]:
                    try:
                        res = tool(**function["arguments"])
                        return res.run(**function["arguments"]), True
                    except ValidationError as e:
                        return str(e.errors()), False
    return "No functions found in the completion."

# class HelloTool(BaseTool):
#     """A tool to greet the user."""
#     user: str = Field(description="The name of the user to greet.")
#     msg : str = Field(description="The message to send to the user.")
#     def run(self, name: str) -> str:
#         """Use the tool."""
#         if not name:
#             raise ValueError("Name cannot be empty.")
#         return f"Hello, {name}!"

#     async def async_run(self, name: str) -> str:
#         """Use the tool asynchronously."""
#         if not name:
#             raise ValueError("Name cannot be empty.")
#         return f"Hello, {name}!"


class BookRecommendation(BaseTool):
    """Provides book recommendations based on specified interest."""
    interest: str = Field(description="The user's interest about a book.")
    recommended_book: str = Field(description="The recommended book.")

    @validator('interest')
    def interest_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Interest cannot be empty.")
        return v

    def run(self, interest: str) -> str:
        """Use the tool."""
        return f"Recommended book for interest {interest} is {self.recommended_book}."

    async def async_run(self, interest: str) -> str:
        """Use the tool asynchronously."""
        return f"Recommended book for interest {interest} is {self.recommended_book}."


# class Joke(BaseTool):
#     """Get a joke that includes the setup and punchline"""
#     setup: str = Field(description="The setup for a joke.")
#     punchline: str = Field(description="The punchline of the joke.")
#     name: str = "Joke"
#     description: str = "Get a joke that includes the setup and punchline"

#     @validator('setup')
#     def setup_must_not_be_empty(cls, v):
#         if not v:
#             raise ValueError("Setup cannot be empty.")
#         return v

#     def run(self, setup: str, punchline: str) -> str:
#         """Use the tool."""
#         print("Joke: aaaaaaaaaa")
#         return f"Joke: {setup}, {punchline}."

#     async def async_run(self, setup: str) -> str:
#         """Use the tool asynchronously."""
#         # return f"Joke: {setup}, {self.punchline}."


# class SongRecommendation(BaseTool):
#     """Provides song recommendations based on specified genre."""
#     genre: str = Field(description="The genre of the song.")
#     song: str = Field(description="The recommended song.")

#     @validator('genre')
#     def genre_must_not_be_empty(cls, v):
#         if not v:
#             raise ValueError("Genre cannot be empty.")
#         return v

#     def run(self, genre: str) -> str:
#         """Use the tool."""
#         return f"Recommended song for genre {genre} is {self.song}."

#     async def async_run(self, genre: str) -> str:
#         """Use the tool asynchronously."""
#         return f"Recommended song for genre {genre} is {self.song}."
    


# class GoogleSearch(BaseTool):
#     """Searches Google for a query."""
#     query: str = Field(description="The query to search Google for.")

#     @validator('query')
#     def query_must_not_be_empty(cls, v):
#         if not v:
#             raise ValueError("Query cannot be empty.")
#         return v

#     def run(self, query: str) -> str:
#         """Use the tool."""

#         # print("GoogleSearch: aaaaaaaaaa")
#         return f"Search Google for query: {query}."

#     async def async_run(self, query: str) -> str:
#         """Use the tool asynchronously."""
#         return f"Search Google for query: {query}."
    

