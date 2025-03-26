from typing import Dict, Any, List
import json
from agent_system.base_agent import BaseAgent
from agent_system.config import AgentConfig

class DataCalibrationTools:
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

class DataCalibrationAgent(BaseAgent):
    def __init__(self, config: AgentConfig, message_bus=None, llm=None):
        super().__init__(config, message_bus, llm)
        self.tools = DataCalibrationTools()
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

    async def process_task(self, task: str) -> Dict[str, Any]:
        """Process a data calibration task using LLM for thinking and mock tools for execution"""
        # 构建提示词，让LLM思考如何处理数据口径任务
        prompt = f"""Given the task: {task}
        Please analyze this task from a data calibration perspective and create:
        1. A semantic search strategy (what data to look for)
        2. A list of business terms and definitions needed
        
        Respond in JSON format with the following structure:
        {{
            "semantic_search_strategy": {{
                "search_terms": ["<term>"],
                "data_domains": ["<domain>"],
                "priority": "<high|medium|low>",
                "reasoning": "<explanation>"
            }},
            "definition_requirements": {{
                "business_terms": ["<term>"],
                "technical_terms": ["<term>"],
                "context": "<usage_context>"
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
            
            # 执行数据口径操作（使用Mock工具）
            search_terms = result.get("semantic_search_strategy", {}).get("search_terms", ["sales data"])
            business_terms = result.get("definition_requirements", {}).get("business_terms", ["total_sales"])
            
            mock_search = self.tools.semantic_search(search_terms[0] if search_terms else "sales data")
            mock_definitions = self.tools.query_definition(business_terms[0] if business_terms else "total_sales")
            
            # 组合结果
            final_result = {
                "semantic_search": mock_search,
                "definitions": mock_definitions,
                "strategy": result.get("semantic_search_strategy", {}),
                "requirements": result.get("definition_requirements", {}),
                "reasoning": result.get("reasoning", ""),
                "status": "completed"
            }
            
            # 记录响应
            self.add_message("assistant", str(final_result))
            return final_result
            
        except json.JSONDecodeError:
            # 如果LLM响应不是有效的JSON，返回模拟数据
            fallback_response = {
                "semantic_search": self.tools.semantic_search("sales data"),
                "definitions": self.tools.query_definition("total_sales"),
                "status": "completed",
                "error": "Failed to parse LLM response"
            }
            self.add_message("assistant", str(fallback_response))
            return fallback_response
