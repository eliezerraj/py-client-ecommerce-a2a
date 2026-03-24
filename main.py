import logging
import asyncio
import boto3

from strands import Agent
from strands.models.bedrock import BedrockModel

from infrastructure.config.config import settings
from infrastructure.tools.factory import create_a2a_tool

from shared.log.logger import setup_logger, REQUEST_ID_CTX
from registry import AgentRegistry

from infrastructure.tools.inventory_a2a import call_inventory_agent
from infrastructure.tools.cart_a2a import call_cart_agent

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
# Main execution function
#---------------------------------
async def run_orchestrator():
    
    print("**** Loading agents...")
    registry = AgentRegistry()
    await registry.register_agent(settings.URL_AGENT_REGISTER_00) # Inventory
    await registry.register_agent(settings.URL_AGENT_REGISTER_01) # Cart
    await registry.register_agent(settings.URL_AGENT_REGISTER_02) # Statistics
    await registry.register_agent(settings.URL_AGENT_REGISTER_03) # K-Means
    skills_context = registry.get_all_skills_as_docs()
    
    print(" **** Available skills in the registry:")
    print(skills_context)

    a2a_tool = create_a2a_tool(registry)

    print("===========================")
    print(a2a_tool)
    print("===========================")

    # Create the supervisor agent
    orchestrator = Agent(
        name="E-Commerce-Orchestrator",
        model=bedrock_model,
        system_prompt=(
            f"You manage e-commerce agents. Available skills: {skills_context}. "
            f"{settings.ORCHESTRATOR_PROMPT}"),
        tools=[a2a_tool]
    )

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

            print('\033[44m *.*.* \033[0m' * 15)
            
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