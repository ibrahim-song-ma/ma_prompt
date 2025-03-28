from typing import Dict, Any, List
import json
from agent_system.base_agent import BaseAgent
from agent_system.config import AgentConfig

class DevelopmentTools:
    """Mock tools for data development"""
    @staticmethod
    def generate_code(description: str) -> Dict[str, Any]:
        return {
            "python": "def process_data(df): return df.groupby('category').sum()",
            "sql": "SELECT category, SUM(amount) FROM sales GROUP BY category"
        }

    @staticmethod
    def test_code(code: str) -> Dict[str, Any]:
        return {"status": "passed", "preview": [{"category": "A", "sum": 100}]}

    @staticmethod
    def validate_code(code: str) -> Dict[str, Any]:
        return {"valid": True, "issues": []}

    @staticmethod
    def query_results(query_id: str) -> Dict[str, Any]:
        return {"status": "completed", "rows": 100, "sample": [{"id": 1, "value": "test"}]}

class DataDeveloperAgent(BaseAgent):
    def __init__(self, config: AgentConfig, message_bus=None, llm=None):
        super().__init__(config, message_bus, llm)
        self.tools = DevelopmentTools()
        self.system_prompt = """You are an AI Data Engineer (Data Development Agent) responsible for:
1. Generating efficient and reliable code
2. Testing and validating implementations
3. Optimizing data processing
4. Ensuring code quality and performance

Your toolbox includes:
- Code Generation Tool: Create Python and SQL code from requirements
- Code Testing Tool: Automated testing and data preview
- Code Validation Tool: Quality checks and error detection
- Result Query Tool: Execute and preview results

Focus on producing high-quality, maintainable, and efficient code while following best practices."""

    def get_system_prompt(self) -> str:
        return self.system_prompt

    async def process_req(self, task: str) -> Dict[str, Any]:
        """Process a development task using LLM for thinking and mock tools for execution"""
        # 构建提示词，让LLM思考如何处理开发任务
        prompt = f"""Given the task: {task}
        Please analyze this task from a data development perspective and create:
        1. A code generation plan (what code needs to be written)
        2. A testing strategy
        3. Validation requirements
        
        Respond in JSON format with the following structure:
        {{
            "code_plan": {{
                "language": "<python|sql>",
                "logic": "<pseudo_code_or_logic>",
                "requirements": ["<requirement>"],
                "dependencies": ["<dependency>"],
                "optimization_points": ["<point>"],
            }},
            "test_strategy": {{
                "test_cases": ["<test_case>"],
                "data_scenarios": ["<scenario>"],
                "validation_points": ["<point>"]
            }},
            "reasoning": "<your thought process>"
        }}
        """
        
        # 调用LLM进行思考
        self.add_message("user", prompt)
        llm_response = await self.llm.generate(
            system_prompt=self.get_system_prompt(),
            messages=self.messages,
            temperature=0.7
        )
        
        try:
            # 解析LLM响应
            result = json.loads(llm_response)
            
            # 执行开发操作（使用Mock工具）
            code_description = result.get("code_plan", {}).get("logic", "Calculate sales by category")
            mock_code = self.tools.generate_code(code_description)
            
            # 执行测试和验证
            test_results = self.tools.test_code(str(mock_code))
            validation_results = self.tools.validate_code(str(mock_code))
            
            # 组合结果
            final_result = {
                "generated_code": mock_code,
                "test_results": test_results,
                "validation": validation_results,
                "development_plan": result.get("code_plan", {}),
                "test_strategy": result.get("test_strategy", {}),
                "reasoning": result.get("reasoning", ""),
                "status": "completed"
            }
            
            # 记录响应
            self.add_message("assistant", str(final_result))
            return final_result
            
        except json.JSONDecodeError:
            # 如果LLM响应不是有效的JSON，返回模拟数据
            fallback_response = {
                "generated_code": self.tools.generate_code("Calculate sales by category"),
                "test_results": self.tools.test_code("mock_code"),
                "validation": self.tools.validate_code("mock_code"),
                "status": "completed",
                "error": "Failed to parse LLM response"
            }
            self.add_message("assistant", str(fallback_response))
            return fallback_response
