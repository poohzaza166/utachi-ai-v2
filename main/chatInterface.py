from typing import Callable

class ChatInterface():
    def __init__(self, callback:  Callable[[str],str], save:  Callable[[str],str], clear:  Callable[[str],str]) -> None:
        self.message = ''
        self.callback = callback
        self.save = save
        self.clear = clear
        
    def start_chat(self):
        while True:
            print('Type a message: ')
            while True:
                line = input()
                if line == '':
                    break
                else:
                    self.message += line
            if '!quit' in self.message:
                break
            if "!save" in self.message:
                self.save()
            if "!clear" in self.message:
                self.clear()
            else:
                print(self.callback(self.message))
                self.message = ''



if __name__ == '__main__':
    chat = ChatInterface()
    chat.start_chat()
