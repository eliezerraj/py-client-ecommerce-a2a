import httpx
from strands import tool

def create_a2a_tool(registry):
    @tool
    async def call_agent_skill(skill_id: str, payload: str) -> str:
        skill_info = registry.skills_map.get(skill_id)
        
        if not skill_info:
            return f"Error: Skill {skill_id} not found."

        payload = {
            "source_agent": "user-postman",
            "target_agent": "inventory-agent",
            "message_type": skill_id,
            "payload": payload
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(skill_info["url"], json=payload)
            return resp.text

    return call_agent_skill