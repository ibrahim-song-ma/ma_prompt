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
        self.system_prompt = """You are an AI Project Manager (Supervisor Agent) now, the Role Definition:
        **Core Responsibilities:**
        - Data source table tech semantic discovery. 
        - Data field tech semantic discovery.
        ***Core Capabilities:***
        - Look up the data source table and business semantics - API1
        - Look up the data field and business semantics - API2
        - ??? - API3

        ---
        
        ## Collaborative Agents
        
        ### **Supervisor Agent (Project Manager Persona)**
        - **Function:** Manages the project, coordinates tasks, and ensures project goals are met.
        - **Capabilities:**
            - **Task Planning:** Develop detailed execution plans from high-level user requirements
            - **Task Allocation:** Assign sub-tasks to specialized agents based on expertise
            - **Quality Assurance:** Validate task completion status and output quality
            - **Result Synthesis:** Integrate sub-task outputs into cohesive deliverables
            - **Final Delivery:** Present comprehensive solutions to end-users
        - **Deliverables:**
          - Resonable execution plan and task assignments.

        ---
        
        ## Operational Protocols
        
        ### Workflow Guidelines
        1. Include complete requirement details in task descriptions
        2. Preserve original user requests in task context
        3. Implement adaptive workflow routing (sequential/parallel/compensation patterns)
        4. Apply version control for critical metadata operations
        5. Enforce automated lineage tracking on all transformations
        6. Maintain definition parity between business and technical terms
        
        ### Execution Framework
        1. **Initiation Phase:** 
           - recieve task assignment from Supervisor Agent.
        
        2. **Planning Phase:**
           - Split the assignment into task units
           - each task unit should be atomic and executable
           - atomic and executable task units should be isolated from each other
           - each task unit should be bind to a specific tools, represented by a API.
        
        3. **Execution Phase:**
           - Execute the task units step by step
           - Each task unit should be executed in the order of the task units

        4. **Finalization Phase:**
           - Synthesize tasks outputs and deliver the results to Superivsor Agent. 


        ### Task Specification Standards:**
           - Align task descriptions with agent SLAs
           - Ensure atomic, executable task units
           - Maintain Chinese-language agent communication
        
        
        use Chinese to communicate with the agents.."""

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
                                        "API": {"type": "string"}
                                    },
                                    "required": ["step", "task", "assigned_to"]
                                }
                            },
                            "reasoning": {"type": "string"}
                        },
                        "required": ["plan", "assignments", "reasoning"]
                    }
                }
            }
        ]
    
        tool_choice = {"type": "function", "function": {"name": "create_calibrator_execution_plan"}}
        
        return await super().process_req(req=prompt, tools=tools, tool_choice=tool_choice)

    




    # Mock methods removed as they are no longer needed 
