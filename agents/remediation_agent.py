from autogen import AssistantAgent

class RemediationAgent(AssistantAgent):
    def __init__(self, name):
        super().__init__(name)
        # self.system_message = """
        # You are a Remediation Agent. Your task is to suggest remediation steps for detected anomalies.
        # - Receive anomalies from the Anomaly Detector Agent.
        # - Analyze the anomalies and suggest appropriate remediation steps.
        # - Pass the remediation steps to the Alerting Agent.
        # """
        # self.update_system_message(self.system_message)

    def suggest_remediation(self, anomalies):
        """Suggest remediation steps for detected anomalies."""
        remediations = []
        for anomaly in anomalies:
            remediation = {
                "anomaly": anomaly,
                "remediation": anomaly.get("Remediation", "No remediation steps available.")
            }
            remediations.append(remediation)
        return remediations

    def run(self):
        """Receive anomalies and suggest remediation steps."""
        while True:
            anomalies = self.receive(from_="anomaly_detector_agent")
            if anomalies:
                remediations = self.suggest_remediation(anomalies)
                # Pass remediations to Alerting Agent
                self.send(remediations, to="alerting_agent")