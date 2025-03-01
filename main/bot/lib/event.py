import os
import importlib
import inspect
import asyncio
import threading
from typing import Callable, Dict, List, Any
from concurrent.futures import ThreadPoolExecutor

class MessageBus:
    def __init__(self):
        # Initialize dictionaries and lists to store various types of callbacks
        self.subscribers: Dict[str, List[Callable]] = {}  # Event subscribers
        self.data_providers: Dict[str, Callable] = {}  # Data provider functions
        self.loop_methods: List[tuple] = []  # Methods to be run in a loop
        self.event_pushers: Dict[str, Callable] = {}  # Event pusher functions

    def subscribe(self, event_name: str, priority: int = 10):
        """Decorator to register a function as a subscriber to a specific event with priority."""
        def decorator(func: Callable):
            if event_name not in self.subscribers:
                self.subscribers[event_name] = []
            self.subscribers[event_name].append((priority, func))
            # Sort subscribers by priority (lower numbers first)
            self.subscribers[event_name].sort(key=lambda x: x[0])
            return func
        return decorator

    def publish(self, event_name: str, *args, **kwargs):
        """Publish an event, calling all subscribers with the provided arguments in priority order."""
        if event_name in self.subscribers:
            for _, subscriber in self.subscribers[event_name]:
                subscriber(*args, **kwargs)

    def provide_data(self, data_name: str):
        """Decorator to register a function as a data provider."""
        def decorator(func: Callable):
            self.data_providers[data_name] = func
            return func
        return decorator

    def get_data(self, data_name: str, *args, **kwargs) -> Any:
        """Retrieve data from a registered data provider."""
        if data_name in self.data_providers:
            return self.data_providers[data_name](*args, **kwargs)
        else:
            raise KeyError(f"No data provider found for '{data_name}'")

    def loop_method(self, delay: float = 0):
        """Decorator to register a method to be run in a loop with a specified delay."""
        def decorator(func: Callable):
            self.loop_methods.append((func, delay))
            return func
        return decorator

    def push_event(self, event_name: str):
        """Decorator to register a function as an event pusher."""
        def decorator(func: Callable):
            self.event_pushers[event_name] = func
            return func
        return decorator

    def trigger_event(self, event_name: str, *args, **kwargs):
        """Trigger an event, calling the associated event pusher and publishing the result."""
        if event_name in self.event_pushers:
            result = self.event_pushers[event_name](*args, **kwargs)
            self.publish(event_name, result)
        else:
            print(f"No event pusher found for '{event_name}'")

class PluginManager:
    def __init__(self, plugin_folder: str):
        self.plugin_folder = plugin_folder
        self.plugins = {}
        self.message_bus = MessageBus()
        self.executor = ThreadPoolExecutor(max_workers=10)

    def load_plugins(self):
        """Load all plugins from the specified plugin folder."""
        for item in os.listdir(self.plugin_folder):
            plugin_path = os.path.join(self.plugin_folder, item)
            if os.path.isdir(plugin_path):
                self._load_plugin(item)

    def _load_plugin(self, plugin_name: str):
        """Load a single plugin by name."""
        try:
            plugin_module = importlib.import_module(f"{self.plugin_folder}.{plugin_name}.main")
            plugin_class = getattr(plugin_module, "PluginInit", None)

            if plugin_class and inspect.isclass(plugin_class):
                plugin_instance = plugin_class()
                if hasattr(plugin_instance, "initialize"):
                    plugin_instance.initialize(self.message_bus)
                    self.plugins[plugin_name] = plugin_instance
                    print(f"Loaded plugin: {plugin_name}")
                else:
                    print(f"Error: Plugin {plugin_name} does not have an initialize method")
            else:
                print(f"Error: Plugin {plugin_name} does not have a valid PluginInit class")
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {str(e)}")

    async def run_plugins(self):
        """Run all loaded plugins and their loop methods asynchronously."""
        tasks = []
        for plugin_name, plugin_instance in self.plugins.items():
            if hasattr(plugin_instance, "run"):
                tasks.append(asyncio.create_task(plugin_instance.run()))
            else:
                print(f"Warning: Plugin {plugin_name} does not have a run method")
        
        for method, delay in self.message_bus.loop_methods:
            tasks.append(asyncio.create_task(self._run_loop_method_async(method, delay)))

        await asyncio.gather(*tasks)

    async def _run_loop_method_async(self, method, delay):
        """Run a loop method asynchronously with the specified delay."""
        loop = asyncio.get_event_loop()
        while True:
            await loop.run_in_executor(self.executor, self._run_method_in_thread, method)
            await asyncio.sleep(delay)

    def _run_method_in_thread(self, method):
        """Execute a method in a separate thread, handling both sync and async methods."""
        try:
            if asyncio.iscoroutinefunction(method):
                asyncio.run(method())
            else:
                method()
        except Exception as e:
            print(f"Error in loop method: {str(e)}")
            print(f"Thread: {threading.current_thread().name}")