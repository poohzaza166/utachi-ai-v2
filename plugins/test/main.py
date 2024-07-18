# plugins/example_plugin/main.py
import asyncio
import time
import threading

class PluginInit:
    def initialize(self, message_bus):
        self.message_bus = message_bus
        
        @message_bus.subscribe("example_event")
        def handle_example_event(message):
            print(f"Example plugin received: {message}")

        @message_bus.subscribe("NewMessage")
        def handle_new_message(user_input):
            print(f"I got a new message: {user_input}")
        
        @message_bus.subscribe("FunctionCallRun")
        @message_bus.provide_data("example_data")
        def provide_example_data(param):
            return f"Example data with param: {param}"
        
        @message_bus.provide_data("NewMessage")
        def provide_new_message(param):
            return f"New message with param: {param}"
        

        @message_bus.loop_method(delay=1)  # Run every 1 second
        async def async_task():
            print(f"Async task running... (Thread: {threading.current_thread().name})")
            await asyncio.sleep(0.5)  # Simulate some async work

        @message_bus.loop_method(delay=2)  # Run every 2 seconds
        def sync_task():
            print(f"Sync task running... (Thread: {threading.current_thread().name})")
            time.sleep(1)  # Simulate some blocking work

    async def run(self):
        print("Example plugin is running")
        while True:
            await asyncio.sleep(10)
            print("Example plugin still active")