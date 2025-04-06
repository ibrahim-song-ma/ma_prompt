from typing import Dict, Any, Optional
from agent_system.base_agent import BaseAgent
from agent_system.config import AgentConfig


class DataEngineeringTools:
    """Tools for data development and pipeline creation"""

    @staticmethod
    def generate_pipeline(requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data pipeline code based on requirements, supporting both Python and SQL"""
        return {
            "python": {
                "extract": "def extract_data(source): return pd.read_csv(source)",
                "transform": "def transform_data(df): return df.groupby('category').sum()",
                "load": "def load_data(df, target): df.to_csv(target)",
            },
            "sql": {
                "extract": "SELECT * FROM source_table",
                "transform": "SELECT category, SUM(amount) FROM sales GROUP BY category",
                "load": "INSERT INTO target_table SELECT * FROM transformed_data",
            },
        }

    @staticmethod
    def validate_pipeline(pipeline: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pipeline code structure and logic, identify potential issues and optimization suggestions"""
        return {
            "valid": True,
            "issues": [],
            "optimizations": [
                "Consider adding error handling",
                "Add logging for pipeline steps",
            ],
        }

    @staticmethod
    def test_pipeline(
        pipeline: Dict[str, Any], sample_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Test pipeline with sample data, return execution status, performance metrics and sample output"""
        return {
            "status": "passed",
            "execution_time": 0.5,
            "memory_usage": "100MB",
            "sample_output": [{"category": "A", "total": 100}],
        }

    @staticmethod
    def optimize_pipeline(pipeline: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize pipeline performance, provide optimized code and improvement suggestions"""
        return {
            "optimized_code": {
                "python": "def optimized_transform(df): return df.groupby('category').agg({'amount': 'sum'})",
                "sql": "SELECT category, SUM(amount) AS total FROM sales GROUP BY category",
            },
            "improvements": [
                "Added explicit column selection",
                "Optimized aggregation function",
            ],
        }

    @staticmethod
    def get_tool_description(method_name: str) -> str:
        return {
            "generate_pipeline": "Generate data pipeline code based on requirements, supporting both Python and SQL",
            "validate_pipeline": "Validate pipeline code structure and logic, identify potential issues and optimization suggestions",
            "test_pipeline": "Test pipeline with sample data, return execution status, performance metrics and sample output",
            "optimize_pipeline": "Optimize pipeline performance, provide optimized code and improvement suggestions",
        }.get(method_name, "Unknown tool")


class DataDeveloperAgent(BaseAgent):
    def __init__(self, config: AgentConfig, message_bus=None, llm=None):
        super().__init__(config, message_bus, llm)
        self.tools = DataEngineeringTools()
        self.system_prompt = """
        # You are an AI Data Engineering Agent

        **Core Responsibilities:**
        - Design and implement data pipelines
        - Generate efficient and reliable code (Python/SQL)
        - Test and validate data transformations
        - Optimize data processing performance
        - Ensure data quality and pipeline reliability

        ---
        
        ## Collaborative Agents
        
        ### **Supervisor Agent (Project Manager Persona)**
        - **Function:** Manages the project, coordinates tasks, and ensures project goals are met.
        - **Collaboration:**
            - Receive task assignments from Supervisor
            - Report progress and issues to Supervisor
            - Deliver final results to Supervisor


        ---
        
        ## Operational Protocols
        
        ### Workflow Guidelines
        1. Receive task assignments from Supervisor
        2. Design pipeline architecture
        3. Implement and test pipeline
        4. Optimize performance
        5. Deliver results to Supervisor
        6. For each step, the result is delivered to the Supervisor for review and approval.
        7. Adjust the workflow as needed based on feedback and requirements.

        ### Execution Framework
        1. **Initiation Phase:** 
           - Receive task from Supervisor
        
        2. **Development Phase:**
           - Design pipeline architecture
           - Implement pipeline components
           - Test and validate pipeline

        3. **Optimization Phase:**
           - Analyze performance
           - Implement optimizations
           - Validate optimizations

        4. **Finalization Phase:**
           - Package and document pipeline
           - Deliver results to Supervisor
           - Provide maintenance guidelines

        ### Task Specification Standards:**
           - Align task descriptions with agent SLAs
           - Ensure atomic, executable task units
           - Maintain Chinese-language agent communication
        
        use Chinese to communicate with the agents.
        """

    def get_system_prompt(self) -> str:
        # Get descriptions of all tools
        tools_desc = "\n## Data Engineering Tools\n"
        for method in [
            "generate_pipeline",
            "validate_pipeline",
            "test_pipeline",
            "optimize_pipeline",
        ]:
            tools_desc += f"- {method}: {self.tools.get_tool_description(method)}\n"

        return self.system_prompt + tools_desc

    async def process_req(self, task: str) -> Dict[str, Any]:
        """Process a data engineering task using LLM for planning and function calling"""
        # Define tools for development planning
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_development_plan",
                    "description": "创建数据工程开发计划",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "requirements": {"type": "string"},
                            "architecture": {
                                "type": "object",
                                "properties": {
                                    "components": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "data_flow": {"type": "string"},
                                    "dependencies": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                            },
                            "implementation": {
                                "type": "object",
                                "properties": {
                                    "steps": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "languages": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "requirements": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                            },
                            "testing": {
                                "type": "object",
                                "properties": {
                                    "test_cases": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "data_scenarios": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "validation_points": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                            },
                            "optimization": {
                                "type": "object",
                                "properties": {
                                    "potential_improvements": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "performance_targets": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                            },
                            "reasoning": {"type": "string"},
                        },
                        "required": [
                            "architecture",
                            "implementation",
                            "testing",
                            "optimization",
                        ],
                    },
                },
            }
        ]

        tool_choice = {
            "type": "function",
            "function": {"name": "create_development_plan"},
        }

        # Process task with tools
        return await super().process_req(req=task, tools=tools, tool_choice=tool_choice)

    async def publish(self, topic: str, message: str):
        """Publish messages to message bus"""
        if self.message_bus:
            await self.message_bus.publish("data_developer", message)
        else:
            print(f"Message Bus not configured. Message: {message}")
