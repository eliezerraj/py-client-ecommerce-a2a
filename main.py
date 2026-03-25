import logging
import asyncio
import boto3
import time

from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.telemetry import StrandsTelemetry
from strands.hooks import (HookProvider, 
                           HookRegistry, 
                           AfterInvocationEvent, 
                           AfterToolCallEvent, 
                           BeforeInvocationEvent, 
                           BeforeToolCallEvent
)

from infrastructure.config.config import settings
from infrastructure.tools.factory import create_a2a_tool
from shared.exception.exceptions import ToolValidationError

from shared.log.logger import setup_logger, REQUEST_ID_CTX
from registry import AgentRegistry

from opentelemetry import trace

#---------------------------------
# Initialize variables from environment
#---------------------------------
print("---" * 15)
print("Starting application with the following settings:")
for key, value in vars(settings).items():
    print(f"{key}: {value}")
print("---" * 15)

#---------------------------------
# Configure logging and telemetry
#---------------------------------
setup_logger(settings.LOG_LEVEL, settings.APP_NAME, settings.OTEL_STDOUT_LOG_GROUP, settings.LOG_GROUP)
logger = logging.getLogger(__name__)

# Set standard OpenTelemetry service name environment variable
strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_otlp_exporter()
strands_telemetry.setup_meter(
    enable_console_exporter=False,
    enable_otlp_exporter=True)
tracer = trace.get_tracer(__name__)

#---------------------------------
# Configure session manager and model/agent
#---------------------------------
# Create boto3 session
session = boto3.Session(
    region_name=settings.REGION,
)

# Create Bedrock model
bedrock_model = BedrockModel(
        model_id=settings.MODEL_ID,
        temperature=0.0,
        boto_session=session,
)

#---------------------------------
# Agent hook setup
#---------------------------------
class AgentHook(HookProvider):

    def __init__(self):
        self.tool_name = settings.APP_NAME
        self.start_agent = ""
        self.tool_calls = 0
        self.metrics = {}

    # Register hooks
    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeInvocationEvent, self.agent_start)
        registry.add_callback(AfterInvocationEvent, self.agent_end)
        registry.add_callback(BeforeToolCallEvent, self.before_tool)
        registry.add_callback(AfterToolCallEvent, self.after_tool)

    # Hook implementations start (get time, log tool usage, collect metrics, etc.)
    def agent_start(self, event: BeforeInvocationEvent) -> None:
        logger.info(f" *** agent_start BeforeInvocationEvent **** ")
        
        self.start_agent = time.time()
        
        cycle_id = "unknown-cycle-id"
            
        # 1. Extract the active OpenTelemetry Trace ID
        current_span = trace.get_current_span()
        trace_id = current_span.get_span_context().trace_id
        
        # Convert numeric trace ID to 32-character hex string, or fallback
        if trace_id:
            cycle_id = f"{trace_id:032x}"
            
        REQUEST_ID_CTX.set(cycle_id)
        
        logger.info(f"Request started - Agent: {event.agent.name} : { self.start_agent }  Request ID: {cycle_id}")

    # Hook implementations end (get time, log tool usage, collect metrics, etc.)
    def agent_end(self, event: AfterInvocationEvent) -> None:
        logger.info(f" *** agent_end AfterInvocationEvent **** ")

        duration = time.time() - self.start_agent
        self.tool_calls = 0  # Reset tool calls here for the next user invocation

        logger.info(f" *** AfterInvocationEvent **** ")

        duration = time.time() - self.start_agent

        logger.info(f"Request completed - Agent: {event.agent.name} - Duration: {duration:.2f}s")
        
        self.metrics["total_requests"] = self.metrics.get("total_requests", 0) + 1
        self.metrics["avg_duration"] = (
            self.metrics.get("avg_duration", 0) * 0.9 + duration * 0.1 # Exponencial Moving Average 
        )

        logger.info(f" *** *** self.metrics *** *** ")
        logger.info(f" {self.metrics}")
        logger.info(f" *** *** self.metrics *** *** ")

    def before_tool(self, event: BeforeToolCallEvent) -> None:
        logger.info(f"*** before_tool BeforeToolCallEvent **** ")
        
        self.tool_calls += 1
        if self.tool_calls > 3:
            raise ToolValidationError("Too many tool calls, aborting to avoid loop")
        
    def after_tool(self, event: AfterToolCallEvent) -> None:
        logger.info(f" *** after_tool AfterToolCallEvent **** ")
        
        self.tool_name = event.tool_use.get("name")
        logger.info(f"* Tool completed - agent: {event.agent.name} : {self.tool_name}")


#---------------------------------
# Main execution function
#---------------------------------
async def run_orchestrator():
    
    print("**** Loading agents...")
    registry = AgentRegistry()
    await registry.register_agent(settings.URL_AGENT_REGISTER_00) # Inventory
    await registry.register_agent(settings.URL_AGENT_REGISTER_01) # Cart
    await registry.register_agent(settings.URL_AGENT_REGISTER_02) # Statistics
    await registry.register_agent(settings.URL_AGENT_REGISTER_03) # K-Means
    
    skills_context_llm = registry.get_skills_context_for_llm()
    
    print(" ---------------------- Skills context for LLM System Prompt ---------------------- ")
    print(skills_context_llm)

    a2a_tool = create_a2a_tool(registry)
    
    # Initialize the agent hook
    agent_hook = AgentHook()

    # Create the orchestrator agent
    orchestrator = Agent(
        name="E-Commerce-Orchestrator",
        model=bedrock_model,
        hooks=[agent_hook],
        system_prompt=(
            f"{settings.ORCHESTRATOR_PROMPT}.\n"
            "CRITICAL: The 'payload' argument for the tool MUST be a valid JSON string "
            "matching the REQUIRED_JSON_STRUCTURE for that skill.\n\n"
            f"Follow the guidelines: {skills_context_llm}. "
        ),
        tools=[a2a_tool],
        callback_handler=None
    )

    print(f'\033[1;33m {settings.APP_NAME} v {settings.VERSION} \033[0m \n')
    print("Type 'quit' to exit. \n")
    print('\033[1;31m Please login before continuing ... \033[0m \n')
     
    # Interactive loop
    while True:
        try:
            print('\033[41m ------------- PROMPT ------------- \033[0m')
            user_input = input("\n> ")
            print('\n\033[41m ------------- PROMPT ------------- \033[0m')

            if user_input.lower() == "exit":
                print("\nGoodbye!")
                #clear_session(session_manager)
                break
            elif user_input.lower() == "quit":
                print("\nGoodbye!")
                #clear_session(session_manager)
                break
            elif user_input.strip() == "":   
                print("Please enter a valid message.")
                continue

            print('\033[1;31m ...Processing... \033[0m \n')    

            response = await orchestrator.invoke_async(user_input.strip())

            print('\n\033[44m ************* AGENT RESPONSE ******************** \033[0m')
            print(f"\n\033[1;32m Agent Response: {response} \033[0m \n")
                                       
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            #clear_session(session_manager)
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try again")
                
if __name__ == "__main__":
    asyncio.run(run_orchestrator())