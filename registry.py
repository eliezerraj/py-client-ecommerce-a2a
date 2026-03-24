import httpx
import asyncio

class AgentRegistry:
    def __init__(self):
        self.agents = {}  # Store full cards
        self.skills_map = {} # Map Skill ID -> Endpoint URL

    async def register_agent(self, base_url: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/.well-known/agent-card.json")
            card = response.json()
            agent_name = card["name"]
            
            # Find the A2A message endpoint
            endpoint = next(
                (iface["url"] for iface in card["supportedInterfaces"] 
                 if iface["protocolBinding"] == "HTTP+JSON"),
                base_url
            )
            
            self.agents[agent_name] = card
            for skill in card.get("skills", []):
                self.skills_map[skill["id"]] = {
                    "url": endpoint,
                    "description": skill["description"],
                    "agent": agent_name
                }
                
    def get_all_skills_as_docs(self):
        # Format for the LLM System Prompt or Tool definitions
        return [
            {"id": k, "description": v["description"]} 
            for k, v in self.skills_map.items()
        ]