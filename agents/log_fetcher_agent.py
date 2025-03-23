import os
import time
from autogen import AssistantAgent

class LogFetcherAgent(AssistantAgent):
    def __init__(self, name, log_folder, fixed_interval_minutes):
        super().__init__(name)
        self.log_folder = log_folder
        print(self.log_folder)
        self.interval = fixed_interval_minutes * 60
        # self.update_config(system_message = f"""
        # You are a Log Fetcher Agent. Your task is to fetch logs from the specified folder at regular intervals.
        # - Fetch logs from the folder: {self.log_folder}.
        # - Send the logs to the Data Ingest Agent for ingestion into the vector database.
        # """)
        # self.update_system_message(self.system_message.format(log_folder=self.log_folder))

    def fetch_logs(self):
        """Fetch logs from the specified folder."""
        logs = []
        for filename in os.listdir(self.log_folder):
            if filename.endswith(".log"):
                with open(os.path.join(self.log_folder, filename), "r") as file:
                    logs.append(file.read())
        return logs

    async def run(self):
        """Run the agent to fetch logs at fixed intervals."""
        while True:
            logs = self.fetch_logs()
            if logs:
                print(f"[{self.name}] Fetched {len(logs)} log files.")
                # Pass logs to the Data Ingest Agent
                self.send(logs, "data_ingest_agent")
            await time.sleep(self.interval)