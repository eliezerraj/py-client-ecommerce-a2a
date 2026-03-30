import re
import json
import httpx
from typing import Dict, Any

class DSLInterpreter:
    def __init__(self, registry):
        self.registry = registry
        # Define Regex patterns for the DSL
        self.patterns = {
            "CHECK_STOCK": r"CHECK STOCK FOR SKU:(?P<sku>[\w-]+)",
            "ANALYZE_RUNOUT": r"ANALYZE RUNOUT SKU:(?P<sku>[\w-]+)",
            "CART_ADD": r"ADD TO CART SKU:(?P<sku>[\w-]+) QTY:(?P<qty>\d+)"
        }

    def parse(self, command: str) -> Dict[str, Any]:
        """Translates DSL string into A2A Skill ID and Payload."""
        for action, pattern in self.patterns.items():
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                groups = match.groupdict()
                
                # Mapping DSL actions to Agent Card Skill IDs
                if action == "ANALYZE_RUNOUT":
                    return {
                        "skill_id": "INVENTORY_RUNOUT_ANALYSIS",
                        "payload": {"product": {"sku": groups["sku"]}}
                    }
                elif action == "CHECK_STOCK":
                    # Example of mapping a simple DSL to a specific internal skill
                    return {
                        "skill_id": "INVENTORY_LEVEL_CHECK",
                        "payload": {"sku": groups["sku"]}
                    }
                elif action == "CART_ADD":
                    return {
                        "skill_id": "CART_UPDATE",
                        "payload": {"items": [{"sku": groups["sku"], "quantity": int(groups["qty"])}]}
                    }
        
        raise ValueError(f"Unknown DSL command: {command}")

    async def execute(self, command: str) -> str:
        """The main entry point for the LLM Tool."""
        try:
            intent = self.parse(command)
            skill_info = self.registry.skills_map.get(intent["skill_id"])
            
            if not skill_info:
                return f"Error: Agent skill {intent['skill_id']} not registered."

            a2a_rpc = {
                "jsonrpc": "2.0",
                "method": "a2a_message",
                "params": {
                    "message_type": intent["skill_id"],
                    "content": intent["payload"]
                },
                "id": "dsl-bridge-v1"
            }

            async with httpx.AsyncClient() as client:
                resp = await client.post(skill_info["url"], json=a2a_rpc)
                return resp.text
        except Exception as e:
            return f"DSL Bridge Error: {str(e)}"