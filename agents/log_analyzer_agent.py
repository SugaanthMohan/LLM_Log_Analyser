from autogen import AssistantAgent
from rag.analyzer import analyse
import datetime
from datetime import timedelta

class LogAnalyzerAgent(AssistantAgent):
    def __init__(self, name, fixed_interval_minutes, app_id):
        super().__init__(name)
        self.interval = fixed_interval_minutes
        self.app_id = app_id
        # self.system_message = """
        # You are a Log Analyzer Agent. Your task is to analyze logs for potential issues.
        # - Receive logs from the Log Fetcher Agent.
        # - Analyze the logs for errors, warnings, or anomalies.
        # - If issues are found, summarize them and pass the results to the Anomaly Detector Agent.
        # - If no issues are found, log the analysis and wait for the next batch of logs.
        # """
        # self.update_system_message(self.system_message)

    def analyze_logs(self, logs):
        """Analyze logs using the RAG implementation."""
        # Get the current time and time 5 minutes ago
        now = datetime.utcnow()
        time_from = now - timedelta(minutes=self.interval)

        # Format as string in the required format
        TIME_FROM = time_from.strftime("%Y-%m-%dT%H:%M:%S")
        TIME_TO = now.strftime("%Y-%m-%dT%H:%M:%S")

        # Call the analyse function with updated times
        result = analyse(self.app_id, TIME_FROM, TIME_TO, "Summarize the logs and look for any anomalies")
        return result

    def run(self):
        """Receive logs from Log Fetcher Agent and analyze them."""
        while True:
            logs = self.receive(from_="log_fetcher_agent")
            if logs:
                analysis_results = self.analyze_logs(logs)
                # Pass analysis results to Anomaly Detector Agent
                self.send(analysis_results, to="anomaly_detector_agent")