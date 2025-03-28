from typing import Dict, Any, List
import json
from agent_system.base_agent import BaseAgent
from agent_system.config import AgentConfig

class CalibrationTools:
    """Mock tools for data calibration"""
    @staticmethod
    def semantic_search(description: str) -> List[Dict[str, Any]]:
        return [{"table": "sales", "relevance": 0.9}, {"table": "customers", "relevance": 0.8}]

    @staticmethod
    def query_definition(field: str) -> Dict[str, Any]:
        return {
            "business_definition": "Total sales amount excluding tax",
            "technical_definition": "SUM(amount) - SUM(tax_amount)"
        }

class CalibratorAgent(BaseAgent):
    def __init__(self, config: AgentConfig, message_bus=None, llm=None):
        super().__init__(config, message_bus, llm)
        self.tools = CalibrationTools()
        self.system_prompt = """You are an AI Data Administrator (Data Calibration Agent) responsible for:
1. Managing enterprise data definitions
2. Providing quick access to business and technical terms
3. Ensuring consistency in data interpretation
4. Supporting semantic data discovery

Your toolbox includes:
- Semantic Search Tool: Find relevant data tables based on descriptions
- Definition Query Tool: Retrieve business and technical definitions

Focus on maintaining accurate and consistent data definitions while supporting business users."""

    def get_system_prompt(self) -> str:
        return self.system_prompt

    async def process_req(self, task: str) -> Dict[str, Any]:
        prompt = f"Given the task: {task}\nPlease analyze this task and create a detailed execution plan with steps and assignments."
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_calibrator_execution_plan",
                    "description": "创建口径查询任务执行计划",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "requirments" :{"type": "string"},
                            "plan": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "step": {"type": "integer"},
                                        "task": {"type": "string"},
                                        "assigned_to": {"type": "string"}
                                    },
                                    "required": ["step", "task", "assigned_to"]
                                }
                            },
                            "assignments": {
                                "type": "object",
                                "additionalProperties": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "reasoning": {"type": "string"}
                        },
                        "required": ["plan", "assignments", "reasoning"]
                    }
                }
            }
        ]
    
        result = await self.process_req_with_tool_calling(
            task=prompt,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "create_execution_plan"}}
        )
        
        if result.get("status") == "error" or "error" in result:
            error_message = result.get("error", "Unknown error in function calling")
            return {
                "status": "error",
                "error": error_message,
                "message": f"Failed to generate task plan: {error_message}"
            }
    
        result["status"] = "in_progress"
    
        return result
    
    def subscribe(self, topic: str):
        self.message_bus.subscribe(topic, self.handle_message)

    def unsubscribe_from(self, topic: str):
        self.message_bus.unsubscribe_all(topic)

    async def handle_message(self, message: Dict[str, Any]) -> None:
        print(f"Calibrator Recieved MSG: {message}")
        self.add_message(role="user", content=message.get("content", ""))




    # Mock methods removed as they are no longer needed 
