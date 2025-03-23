from autogen import GroupChat, GroupChatManager
from .log_fetcher_agent import LogFetcherAgent
from .data_ingest_agent import DataIngestAgent
from .log_analyzer_agent import LogAnalyzerAgent
from .anomaly_detector_agent import AnomalyDetectorAgent
from .remediation_agent import RemediationAgent
from .alerting_agent import AlertingAgent

class AgentOrchestrator:
    def __init__(self, app_id, fixed_interval_minutes=5):
        self.log_fetcher_agent = LogFetcherAgent("log_fetcher_agent", f"data/logs/{app_id}", fixed_interval_minutes)
        self.data_ingest_agent = DataIngestAgent("data_ingest_agent", app_id)
        self.log_analyzer_agent = LogAnalyzerAgent("log_analyzer_agent", fixed_interval_minutes, app_id)
        self.anomaly_detector_agent = AnomalyDetectorAgent("anomaly_detector_agent")
        self.remediation_agent = RemediationAgent("remediation_agent")
        # self.alerting_agent = AlertingAgent("alerting_agent", "gowsiman@gmail.com", "your_password")

        self.agents = [
            self.log_fetcher_agent,
            self.data_ingest_agent,
            self.log_analyzer_agent,
            self.anomaly_detector_agent,
            self.remediation_agent,
            # self.alerting_agent,
        ]

        self.group_chat = GroupChat(agents=self.agents, messages=[])
        self.manager = GroupChatManager(groupchat=self.group_chat)

    def run(self):
        """Start all agents."""
        for agent in self.agents:
            agent.run()