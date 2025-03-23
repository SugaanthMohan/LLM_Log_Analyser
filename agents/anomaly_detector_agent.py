from autogen import AssistantAgent

class AnomalyDetectorAgent(AssistantAgent):
    def __init__(self, name):
        super().__init__(name)
        # self.system_message = """
        # You are an Anomaly Detector Agent. Your task is to detect anomalies in log analysis results.
        # - Receive analysis results from the Log Analyzer Agent.
        # - Compare the results with historical data to detect anomalies.
        # - If anomalies are found, pass them to the Remediation Agent.
        # - If no anomalies are found, log the results and wait for the next batch.
        # """
        # self.update_system_message(self.system_message)

    def detect_anomalies(self, analysis_results):
        """Detect anomalies using the provided prompt."""
        anomalies = []
        if "error" in analysis_results.lower():
            anomalies.append(analysis_results)
        return anomalies

    def run(self):
        """Receive analysis results and detect anomalies."""
        while True:
            analysis_results = self.receive(from_="log_analyzer_agent")
            if analysis_results:
                anomalies = self.detect_anomalies(analysis_results)
                if anomalies:
                    # Pass anomalies to Remediation Agent
                    self.send(anomalies, to="remediation_agent")