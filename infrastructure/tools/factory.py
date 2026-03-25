import json
import logging
import httpx
import uuid

from jsonschema import ValidationError, validate
from strands import tool
from opentelemetry.propagate import inject

from shared.log.logger import REQUEST_ID_CTX

#---------------------------------
# Configure logging
#---------------------------------
logger = logging.getLogger(__name__)

# create the headers for the outgoing HTTP request, including a unique x-request-id and propagating OpenTelemetry context
def _set_headers() -> dict:
    headers = {
        "x-request-id": REQUEST_ID_CTX.get() if REQUEST_ID_CTX else str(uuid.uuid4()),
        "Content-Type": "application/json"
    }
    inject(headers)
    return headers

# Factory function to create the call_agent_skill tool with access to the agent registry for skill validation
def create_a2a_tool(registry):
    @tool
    async def call_agent_skill(skill_id: str, payload: str) -> str:
        logger.info("def call_agent_skill()")
        
        # Validate skill_id exists in registry        
        skill_info = registry.skills_map.get(skill_id)
        
        if not skill_info:
            return f"Error: Skill {skill_id} not found."

        # Validate payload is a valid JSON string
        try:
            payload_dict = json.loads(payload)
        except json.JSONDecodeError:
            return "Error: Payload must be a valid JSON string."

        # If the skill has an input schema, validate the payload against it
        if "inputSchema" in skill_info:
            try:
                validate(instance=payload_dict, schema=skill_info["inputSchema"])
            except json.JSONDecodeError:
                return "Error: You must provide a valid JSON string as the payload."
            except ValidationError as e:
                return f"Error: Payload does not match schema. {e.message}"
                    
        payload = {
            "source_agent": "user-postman",
            "target_agent": "inventory-agent",
            "message_type": skill_id,
            "payload": payload_dict
        }

        print("---"*20)
        print(f"Calling skill {skill_id} at {skill_info['url']} with payload:")
        print(json.dumps(payload, indent=2))
        print("---"*20)
        
        # Make the HTTP POST request to the agent's skill endpoint    
        async with httpx.AsyncClient() as client:
            resp = await client.post(skill_info["url"], 
                                     json=payload,
                                     headers=_set_headers())
            return resp.text

    return call_agent_skill