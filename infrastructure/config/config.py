import os
from dotenv import load_dotenv

load_dotenv(".env")

class Settings:
    def __init__(self):
        self.VERSION = os.getenv("VERSION")
        self.ACCOUNT = os.getenv("ACCOUNT")
        self.APP_NAME = os.getenv("APP_NAME")
        self.MODEL_ID = os.getenv("MODEL_ID")
        self.REGION = os.getenv("REGION")
        self.SESSION_ID = os.getenv("SESSION_ID", "eliezer-001")

        self.URL_AGENT_REGISTER_00 = os.getenv("URL_AGENT_REGISTER_00")
        self.URL_AGENT_REGISTER_01 = os.getenv("URL_AGENT_REGISTER_01")
        self.URL_AGENT_REGISTER_02 = os.getenv("URL_AGENT_REGISTER_02")
        self.URL_AGENT_REGISTER_03 = os.getenv("URL_AGENT_REGISTER_03")
        
        self.OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        self.OTEL_STDOUT_LOG_GROUP = os.getenv("OTEL_STDOUT_LOG_GROUP", "false").lower() == "true"
        self.LOG_GROUP = os.getenv("LOG_GROUP")

        self.ORCHESTRATOR_PROMPT = """
            You are a coordinator for Inventory and Cart agents.
            
            Available Tools Agents:
            - inventory_a2a_agent
            - cart_a2a_agent
            
            Tool Usage Rules:
            1. All questions related to inventory and cart management should be directed to the appropriate agent.
            2. Use the tools provided to communicate with the sub-agents.
            
            Response Rules:
            1. Tool outputs are authoritative.
            2. Do NOT re-call tools to “confirm” results.
            3. Do NOT modify field names or formats returned by tools.
            4. Return a final user-facing answer after tool execution.
            
            Failure Rules:
            1. If a tool returns an error, report it and STOP.
        """
        
settings = Settings()
