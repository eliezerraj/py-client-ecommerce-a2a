import logging
import os
import shutil
import boto3

from strands import Agent, tool
from strands.models import BedrockModel
from strands.agent.a2a_agent import A2AAgent
from strands.session.file_session_manager import FileSessionManager
from strands.agent.conversation_manager import SlidingWindowConversationManager

from infrastructure.config.config import settings
from shared.log.logger import setup_logger, REQUEST_ID_CTX

#---------------------------------
# Initialize variables from environment
#---------------------------------
print("---" * 15)
print("Starting application with the following settings:")
for key, value in vars(settings).items():
    print(f"{key}: {value}")
print("---" * 15)

#---------------------------------
# Configure logging
#---------------------------------
setup_logger(settings.LOG_LEVEL, settings.APP_NAME, settings.OTEL_STDOUT_LOG_GROUP, settings.LOG_GROUP)
logger = logging.getLogger(__name__)

logger.info('\033[1;33m Starting the Main Agent... \033[0m')
logger.info(f'\033[1;33m model_id: {settings.MODEL_ID} \033[0m \n')

MAIN_SYSTEM_PROMPT = """
    You are MAIN agent an orchestrator designed to coordinate support across multiple agents.

    Available Tools Agents:
    - inventory_a2a_agent
    - cart_a2a_agent
    - calculator

    Tool Usage Rules:
    - Use MCP tools ONLY when required to answer the user query.
    - NEVER call the same tool more than once for the same request.
    - After a tool successfully returns the required data, STOP and return a final response.
    - If no tool is required, answer directly.

    Response Rules:
    - Tool outputs are authoritative.
    - Do NOT re-call tools to “confirm” results.
    - Do NOT modify field names or formats returned by tools.
    - Return a final user-facing answer after tool execution.

    Termination Rules (VERY IMPORTANT):
    - Once the required information is obtained from a tool, do NOT call any more tools.
    - Produce a final response immediately.

    Failure Rules:
    - If a tool returns an error, report it and STOP.
"""

#---------------------------------
# Configure session manager
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

# Create a session manager with a unique session ID
session_manager = FileSessionManager(session_id=settings.SESSION_ID,
                                     storage_dir="./sessions")

# Create a conversation manager with custom window size
conversation_manager = SlidingWindowConversationManager(
    window_size=20,  # Maximum number of messages to keep
    should_truncate_results=True, # Enable truncating the tool result when a message is too large for the model's context window 
)

agent_main = Agent(name="main",
                   system_prompt=MAIN_SYSTEM_PROMPT, 
                   model=bedrock_model,
                   conversation_manager=conversation_manager,
                   session_manager=session_manager,
                   callback_handler=None)

# Clear session files
def clear_session(session_manager):
    session_dir  = os.path.join(session_manager.storage_dir, f"session_{session_manager.session_id}")
    
    logger.info(f"Cleaning session files: {session_dir }")

    # 2. Check if the directory exists
    if os.path.isdir(session_dir):
        try:
            shutil.rmtree(session_dir)
        except Exception as e:
            logger.error(f"Failed to delete {session_dir}. Reason: {e}")

        logger.info(f"All files in {session_dir} cleared for session {session_manager.session_id}.")
    else:
        logger.info(f"Directory not found: {session_dir}")

#---------------------------------
# Initialize the agent
#---------------------------------    


async def run_orchestrator():

    
if __name__ == "__main__":
    print(f'\033[1;33m {settings.APP_NAME} v {settings.VERSION} \033[0m \n')
    print("Type 'exit' to quit. \n")
    print('\033[1;31m Please login before continuing ... \033[0m \n')
    
    # Interactive loop
    while True:
        try:
            print('\033[41m =.=.= \033[0m' * 15)
            user_input = input("\n> ")
            print('\033[41m =.=.= \033[0m' * 15)

            if user_input.lower() == "exit":
                print("\nGoodbye!")
                clear_session(session_manager)
                break
            elif user_input.lower() == "quit":
                print("\nGoodbye!")
                clear_session(session_manager)
                break
            elif user_input.strip() == "":   
                print("Please enter a valid message.")
                continue

            print('\033[1;31m ...Processing... \033[0m \n')    

            response = agent_main(user_input.strip())

            print('\033[44m *.*.* \033[0m' * 15)
            
            print(f"\n\033[1;32m Agent Response: {response} \033[0m \n")
                                       
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            clear_session(session_manager)
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try again")