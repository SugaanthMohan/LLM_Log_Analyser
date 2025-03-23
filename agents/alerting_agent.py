import smtplib
from email.mime.text import MIMEText
from autogen import AssistantAgent

class AlertingAgent(AssistantAgent):
    def __init__(self, name, email, password):
        super().__init__(name)
        self.email = email
        self.password = password
        # self.system_message = """
        # You are an Alerting Agent. Your task is to send email alerts for detected anomalies and their remediation steps.
        # - Receive remediation steps from the Remediation Agent.
        # - Format the information into an email.
        # - Send the email to the specified recipient.
        # """
        # self.update_system_message(self.system_message)

    def send_email(self, subject, body):
        """Send an email alert."""
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.email
        msg["To"] = self.email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(self.email, self.password)
            server.sendmail(self.email, self.email, msg.as_string())

    def run(self):
        """Receive remediations and send email alerts."""
        while True:
            remediations = self.receive(from_="remediation_agent")
            if remediations:
                for remediation in remediations:
                    subject = "Anomaly Detected in Logs"
                    body = f"Anomaly: {remediation['anomaly']}\nRemediation: {remediation['remediation']}"
                    print(subject)
                    print(body)
                    # self.send_email(subject, body)
                    print(f"[{self.name}] Email alert sent.")