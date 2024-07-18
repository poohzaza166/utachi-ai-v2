from datetime import datetime
from main.bot.lib.tools import BaseTool


class timeTool(BaseTool):
    """Use this tool to get the current time"""

    def run(self):

        return f"The current system time is {datetime.now()}"
