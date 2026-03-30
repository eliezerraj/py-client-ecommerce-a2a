import httpx
import asyncio

class AgentRegistry:
    
    def __init__(self):
        self.agents = {}  # Store full cards
        self.skills_map = {} # Map Skill ID -> Endpoint URL

    # Registers an agent by fetching its card and extracting skills. Using input_schema and examples to provide richer context for LLMs.
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
                    "agent": agent_name,
                    "url": endpoint,
                    "description": skill["description"],
                    "input_schema": skill.get("inputSchema"),
                    "example": skill.get("examples"),
                }
                
    def get_skills_context_for_llm(self):
        """Formats a concise guide for the LLM system prompt."""
        context = "AVAILABLE SKILLS AND THEIR SCHEMAS:\n"
        for sid, info in self.skills_map.items():
            context += f"- SKILL_ID: {sid}\n"
            context += f"  DESCRIPTION: {info['description']}\n"
            context += f"  REQUIRED_JSON_STRUCTURE: {info['input_schema']}\n"
            context += f"  EXAMPLE_PAYLOAD: {info['example']}\n\n"
        return context