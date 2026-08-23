from google.adk.apps import App, ResumabilityConfig
from . import agent

app = App(
    name="expense_agent",
    root_agent=agent.root_agent,
    resumability_config=ResumabilityConfig(enabled=True)
)
