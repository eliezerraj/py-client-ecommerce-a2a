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
async def call_cart_agent(action: str) -> str:
    """
    Queries the Cart agent to add, remove, or list items.
    Args:
        action: The specific cart instruction (e.g., 'Add 2 laptops to cart').
    """
    url = "http://localhost:8001/a2a/message"
    payload = {
        "jsonrpc": "2.0",
        "method": "a2a_message",
        "params": {"text": action},
        "id": 1
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        return response.json().get("result", "No response from Cart")