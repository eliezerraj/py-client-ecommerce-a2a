import logging
import httpx
from strands import tool
from infrastructure.config.config import settings

#---------------------------------
# Configure logging
#---------------------------------
logger = logging.getLogger(__name__)

async def load_agent_card(self, base_url: str):
    async with httpx.AsyncClient() as client:
        logger.info("func.load_agent_card()")

        response = await client.get(f"{base_url}/.well-known/agent-card.json")
        if response.status_code == 404:
            
            response = await client.get(f"{base_url}/.well-known/agent-card.json")

            response.raise_for_status()
            card = response.json()

    return card

@tool
async def call_inventory_agent(query: str) -> str:
    
    url = "http://localhost:8000/a2a/message"
    payload = {
        "source_agent": "user-postman",
        "target_agent": "inventory-agent",
        "message_type": "INVENTORY_RUNOUT_ANALYSIS",
        "payload": {
            "product": {
                "sku": "cheese-fr-12"
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        
        print(f"Inventory Agent Response: {response.json()}")
        
        return response.json().get("payload", "No response from Inventory")