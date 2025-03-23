import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from agents.agent_orchestrator import AgentOrchestrator

if __name__ == "__main__":
    app_id = "APP_4"  # Replace with your application ID
    fixed_interval_minutes = 5  # Set the fixed interval for analysis
    orchestrator = AgentOrchestrator(app_id, fixed_interval_minutes)
    orchestrator.run()