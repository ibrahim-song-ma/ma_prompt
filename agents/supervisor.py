from typing import Dict, Any, List
from agent_system.base_agent import BaseAgent
from agent_system.config import AgentConfig

class SupervisorAgent(BaseAgent):
    def __init__(self, config: AgentConfig, message_bus=None, llm=None):
        super().__init__(config, message_bus, llm)
        self.system_prompt = """
        # You are an AI Project Manager (Supervisor Agent), the Role Definition

        **Core Responsibilities:**
        - **Task Planning:** Develop detailed execution plans from high-level user requirements
        - **Task Allocation:** Assign sub-tasks to specialized agents based on expertise
        - **Quality Assurance:** Validate task completion status and output quality
        - **Result Synthesis:** Integrate sub-task outputs into cohesive deliverables
        - **Final Delivery:** Present comprehensive solutions to end-users
        
        ---
        
        ## Collaborative Agents
        
        ### **Data Calibrator Agent (Data Administrator Persona)**
        - **Function:** Manages business terminology and metric definitions
        - **Capabilities:**
          - Data source table/field discovery
          - Technical & business semantic resolution
        - **Deliverables:**
          - Source table/field catalog
          - Field/metric calculation logic
          - Business semantic specifications
          - Data unit conventions
        
        ### **Data Engineering Agent (Data Development Engineer Persona)**
        - **Function:** Develops code and data pipelines per requester specifications
        - **Capabilities:**
          - SQL/Python code generation
          - Code testing & debugging
          - Result validation
        - **Deliverables:**
          - Production-grade SQL/Python code
          - Data pipeline architecture
          - Validation reports with query results
        

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
           - Route all user requirements through Data Calibrator
           - Validate calibration outputs before progression
        
        2. **Development Phase:**
           - Sequentially route calibrated specs to Data Engineering Agent
           - Implement phased delivery with interim validation
        
        3. **Governance Controls:**
           - Activate Data Governance Agent only on usr explicit request it
           - Apply automated quality gates between phases

        4. **Finalization Phase:**
           - Create a temporary table for the Supervisor Agent to deliver the final results
           - Supervisor Agent to synthesize all outputs and deliver the results to the user. 


        ### Task Specification Standards:**
           - Align task descriptions with agent SLAs
           - Ensure atomic, executable task units
           - Maintain Chinese-language agent communication
        
        ---
        
        ## Quality Assurance Measures
        - Implement bi-directional traceability matrix
        - Conduct pre-execution capability matching
        - Enforce schema validation checkpoints
        - Apply automated consistency checks
        - Maintain audit trails for critical operations
        
        (Note: Corrected all spelling errors and standardized technical terminology. Enhanced structural clarity while preserving original functionality. Added quality assurance section for improved operational rigor.)
        
        use Chinese to communicate with the agents.
"""

    def get_system_prompt(self) -> str:
        """获取SupervisorAgent的系统提示词"""
        return self.system_prompt

    async def process_req(self, req: str) -> Dict[str, Any]:
        """Process a project management task using LLM for thinking and function calling"""
        # 构建提示词，让LLM思考如何处理任务
        prompt = f"Given the task: {req}\nPlease analyze this task and create a detailed execution plan with steps and execute step by step."
        
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
        
        return await super().process_req(req=prompt, tools=tools, tool_choice=tool_choice)

    async def publish(self, topic: str, message: str):
        messagebus = self.message_bus
        if messagebus:
            await messagebus.publish('supervisor', message)
        else:
            print(f"Message Bus not configured. Message: {message}")

   
    def prepare_calibrator_msg(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare message for Data Calibrator Agent"""
        arguments = result.get("arguments", {})
        if not arguments:
            return {"error": "No arguments found in result"}

        if "assignments" not in arguments:
            return {"instruction": "No assignments found in result"}
        
        calibrate_assignments = {
            key: value for key, value in arguments.get("assignments",{}).items() 
            if "calibrator" in key.lower() or "calibration" in key.lower()
        }

        if not calibrate_assignments:
            return {"error": "No calibrator-related assignments found"}

        message = ""
        for key, tasks in calibrate_assignments.items():
            message += f"{key}:\n"
            for task in tasks:
                message += f"- {task}\n"

        return {
            "instruction": "Data Calibrator Agent, please process the following assignments and requirements",
            "requirements": arguments.get("requirments", ""),
            "assignments": message
        }
