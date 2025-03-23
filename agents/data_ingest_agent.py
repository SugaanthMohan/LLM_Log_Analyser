from autogen import AssistantAgent
from rag.analyzer import init  
from db.create_database import generate_data_store  
import os

class DataIngestAgent(AssistantAgent):
    def __init__(self, name, app_id):
        super().__init__(name)
        self.app_id = app_id
        # self.system_message = """
        # You are a Data Ingest Agent. Your task is to ingest new log data into the vector database.
        # - Receive logs from the Log Fetcher Agent.
        # - Check if the logs already exist in the vector database.
        # - Ingest only new logs into the vector database.
        # - Pass the ingested logs to the Log Analyzer Agent for analysis.
        # """
        # self.update_system_message(self.system_message)

        # Initialize the vector database
        self.llm, self.db = init(self.app_id)

    def is_log_new(self, log):
        """
        Check if a log already exists in the vector database.
        Args:
            log (str): The log entry to check.
        Returns:
            bool: True if the log is new, False if it already exists.
        """
        # Search the vector database for similar logs
        results = self.db.similarity_search(log, k=1)
        if results:
            # If a similar log exists, compare the content
            existing_log = results[0].page_content
            return log.strip() != existing_log.strip()
        return True  # Log is new if no similar logs are found

    def ingest_logs(self, logs):
        """
        Ingest new logs into the vector database.
        Args:
            logs (list): List of log entries to ingest.
        Returns:
            list: List of newly ingested logs.
        """
        new_logs = [log for log in logs if self.is_log_new(log)]
        if new_logs:
            # Ingest new logs into the vector database
            generate_data_store(self.app_id, "data/logs", f"db/chroma/{self.app_id}", self.llm)
        return new_logs

    def run(self):
        """Receive logs from Log Fetcher Agent, ingest them, and pass them to Log Analyzer Agent."""
        while True:
            logs = self.receive(sender="log_fetcher_agent")
            print(logs)
            if logs:
                new_logs = self.ingest_logs(logs)
                if new_logs:
                    print(f"[{self.name}] Ingested {len(new_logs)} new log entries into the vector database.")
                    # Pass newly ingested logs to Log Analyzer Agent
                    self.send(new_logs, "log_analyzer_agent")
                else:
                    print(f"[{self.name}] No new logs to ingest.")