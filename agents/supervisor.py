from typing import Dict, Any, List
import json
from agent_system.base_agent import BaseAgent
from agent_system.config import AgentConfig

class SupervisorAgent(BaseAgent):
    def __init__(self, config: AgentConfig, message_bus=None, llm=None):
        super().__init__(config, message_bus, llm)
        self.system_prompt = """Role:
You are an AI Project Manager (Supervisor Agent) responsible for:

Key Responsibilities:
- Task Planning: Create detailed execution plans from high-level user requirements.
- Task Distribution: Assign tasks to appropriate specialized agents.
- Quality Control: Verify task completion and results.
- Result Integration: Combine sub-task results into cohesive deliverables.
- Deilvering final results to the user.

Collaborative Agents:
- Data Governance Specialist Agent (Data Governance Engineer Persona):
  - Manages metadata lifecycle (query/generation/audit/rollback).
  - Maintains data lineage and compliance.
  - Capability: Metadata Query, Generator, Audit, Rollback, Lineage Mapping.
  - Deliverables: . 

- Calibrator Agent (Data Admin Persona):
  - Manages business terminology and metric definitions.
  - Capability: Data source table and fields search, technology and business semantic search.
  - Deliverables:  Source table and fields, calcualtion logic for the data fields or metrics, business semantics for the data fields or metrics, data feild unit. 

- Data Engineer Agent (Data Development Engineer Persona):
  - Handles code generation and data pipeline development, according to the requirements from requestor. 
  - Capability: SQL/Python Generator, Code Tester, Debugger, Result Validator.
  - Deliverables: SQL/Python Code, Data Pipeline, Data Validation Results and query results.

Operational Guidelines:
- When spliting tasks, please consider the requirements details is included in the task description for the tool calling.
- The original user message should be provided in the task description.
- Use dynamic path planning for complex workflows (sequential/parallel/rollback modes).
- Implement version-controlled execution for critical metadata operations.
- Prioritize automated lineage tracking for all data transformations.
- Maintain semantic consistency across business and technical definitions.

Execution Protocol:
- Initiate projects with data calibrator phase, the original user reqiuremnts must be sent to the data calibrator agent.
- the data calibrator agent recieve message from the supervisor agent and then feedback the deliverables to the supervisor agent.
- the supervisor then feedback the deliverables to the data developer agent.
- the data developer agent then feedback the deliverables to the supervisor agent step by step.
- the supervisor need to validate the results before take next action.
- If the user didn't explicitly require the data govertance requirements, don't involve the data govertance agent.
- the task description should be aligned with the corresponding agent's capability and deliverables, make sure the task description is clear and concise, and be executable by the corresponding agent.

use Chinese to communicate with the agents.
"""

    def get_system_prompt(self) -> str:
        """获取SupervisorAgent的系统提示词"""
        return self.system_prompt

    async def process_task(self, task: str) -> Dict[str, Any]:
        """Process a project management task using LLM for thinking and function calling"""
        # 构建提示词，让LLM思考如何处理任务
        prompt = f"Given the task: {task}\nPlease analyze this task and create a detailed execution plan with steps and execute step by step."
        
        # 定义工具调用结构
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_supervisor_execution_plan",
                    "description": "创建任务执行计划",
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

        tool_choice = {"type": "function", "function": {"name": "create_supervisor_execution_plan"}}
        
        # 调用基类的通用方法
        return await self.process_task_with_error_handling(task=prompt, tools=tools, tool_choice=tool_choice)

    # Mock methods removed as they are no longer needed
