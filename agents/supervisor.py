from typing import Dict, Any, List
import json
from agent_system.base_agent import BaseAgent
from agent_system.config import AgentConfig

class SupervisorAgent(BaseAgent):
    def __init__(self, config: AgentConfig, message_bus=None, llm=None):
        super().__init__(config, message_bus, llm)
        self.system_prompt = """You are an AI Project Manager (Supervisor Agent) responsible for:
        1. Accepting and analyzing project requirements
        2. Breaking down tasks into executable sub-tasks
        3. Coordinating with other specialized agents
        4. Validating results and adjusting plans as needed
        5. Delivering final results to users

        Your key responsibilities:
        - Task Planning: Create detailed execution plans from high-level requirements
        - Task Distribution: Assign tasks to appropriate specialized agents
        - Quality Control: Verify task completion and results
        - Result Integration: Combine sub-task results into cohesive deliverables

        Always maintain a professional and organized approach to project management."""

    def get_system_prompt(self) -> str:
        return self.system_prompt

    async def process_task(self, task: str) -> Dict[str, Any]:
        """Process a project management task using LLM for thinking and function calling"""
        # 构建提示词，让LLM思考如何处理任务
        prompt = f"Given the task: {task}\nPlease analyze this task and create a detailed execution plan with steps and assignments."
        
        # 定义工具调用结构
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_execution_plan",
                    "description": "创建任务执行计划",
                    "parameters": {
                        "type": "object",
                        "properties": {
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
        
        # 使用父类的函数调用方法
        result = await self.process_task_with_tool_calling(
            task=prompt,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "create_execution_plan"}}
        )
        
        # 如果函数调用出错，直接返回错误
        if result.get("status") == "error" or "error" in result:
            error_message = result.get("error", "Unknown error in function calling")
            return {
                "status": "error",
                "error": error_message,
                "message": f"Failed to generate task plan: {error_message}"
            }
        
        # 添加状态信息
        result["status"] = "in_progress"
        
        return result

    # Mock methods removed as they are no longer needed
