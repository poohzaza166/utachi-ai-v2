import json
import re

def parse_function_call(text):
    # Try to parse as JSON first
    try:
        data = json.loads(text)
        if isinstance(data, dict) and 'function_call' in data:
            return parse_json_function_call(data['function_call'])
    except json.JSONDecodeError:
        pass

    # If not JSON, try to extract function call using regex
    return parse_text_function_call(text)

def parse_json_function_call(function_call):
    if isinstance(function_call, str):
        try:
            function_call = json.loads(function_call)
        except json.JSONDecodeError:
            return {'error': 'Invalid function_call format'}

    name = function_call.get('name', '')
    arguments = function_call.get('arguments', '')

    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            pass  # Keep arguments as string if it's not valid JSON

    return {
        'name': name,
        'arguments': arguments
    }

def parse_text_function_call(text):
    function_match = re.search(r'"function_call"\s*:\s*({[^}]*})', text)

    if not function_match:
        return {'error': 'No function call found'}

    function_content = function_match.group(1)
    try:
        function_call = json.loads(function_content)
        return parse_json_function_call(function_call)
    except json.JSONDecodeError:
        # If JSON parsing fails, try regex
        name_match = re.search(r'"name"\s*:\s*"([^"]*)"', function_content)
        args_match = re.search(r'"arguments"\s*:\s*([\'"])((?:(?!\1).)*)\1', function_content)

        name = name_match.group(1) if name_match else ''
        arguments = args_match.group(2) if args_match else ''

        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            pass  # Keep arguments as string if it's not valid JSON

        return {
            'name': name,
            'arguments': arguments
        }

# Test cases
test_cases = [
    '{ "message": "Here are the latest news headlines for the United States:", "function_call": {"name": "get_news_headlines", "arguments": {"country": "France"}} }',
    '{ "message": "Here are the latest news headlines for the United States:", "function_call": "{\"name\": \"get_news_headlines\", \"arguments\": \'{\"country\": \"France\"}\'}" }',
    'The message is "Here are the latest news headlines for the United States:" and the function_call is {"name": "get_news_headlines", "arguments": \'{"country": "France"}\'}',
]

for i, case in enumerate(test_cases, 1):
    print(f"Test case {i}:")
    print(parse_function_call(case))
    print()