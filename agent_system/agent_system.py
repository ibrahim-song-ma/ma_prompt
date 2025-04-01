from typing import Dict, Any, List
import asyncio
from .config import load_config, AgentConfig
from .llm import DeepSeekLLM
from .message_bus import MessageBus
from agents.supervisor import SupervisorAgent
from agents.metadata_steward import MetadataStewardAgent
from agents.calibrator import CalibratorAgent
from agents.developer import DataDeveloperAgent

class AgentSystem:
    def __init__(self):
        self.config = load_config()
        self.message_bus = MessageBus()
        self.llm = DeepSeekLLM(self.config)
        
        self.supervisor = SupervisorAgent(
            config=AgentConfig(
                name="Supervisor", 
                description="Project Manager", 
                role="supervisor",
                llm_config=self.config
            ),
            message_bus=self.message_bus,
            llm=self.llm
        )
        
        self.metadata_steward = MetadataStewardAgent(
            config=AgentConfig(
                name="Metadata Steward", 
                description="Data Governance Engineer", 
                role="metadata_steward",
                llm_config=self.config
            ),
            message_bus=self.message_bus,
            llm=self.llm
        )
        
        self.data_calibration = CalibratorAgent(
            config=AgentConfig(
                name="Data Calibration", 
                description="Data Administrator", 
                role="data_calibration",
                llm_config=self.config
            ),
            message_bus=self.message_bus,
            llm=self.llm
        )
        
        self.data_developer = DataDeveloperAgent(
            config=AgentConfig(
                name="Data Developer", 
                description="Data Engineer", 
                role="data_developer",
                llm_config=self.config
            ),
            message_bus=self.message_bus,
            llm=self.llm
        )
        
        # 初始化Agent编排配置
        self.workflow = {
            "supervisor": {
                "next": ["metadata_steward", "data_calibration"],
                "wait_for": []
            },
            "metadata_steward": {
                "next": ["data_developer"],
                "wait_for": ["supervisor"]
            },
            "data_calibration": {
                "next": ["data_developer"],
                "wait_for": ["supervisor"]
            },
            "data_developer": {
                "next": [],
                "wait_for": ["metadata_steward", "data_calibration"]
            }
        }
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        """Process a task through the multi-agent system"""
        results = {}
        
        # 1. 启动Supervisor
        supervisor_result = await self.supervisor.process_req(task)
        results["supervisor"] = supervisor_result
        
        # 2. 并行执行元数据和数据口径任务
        metadata_task = asyncio.create_task(self.metadata_steward.process_req(task))
        calibration_task = asyncio.create_task(self.data_calibration.process_task(task))
        
        metadata_result, calibration_result = await asyncio.gather(
            metadata_task,
            calibration_task
        )
        
        results["metadata_steward"] = metadata_result
        results["data_calibration"] = calibration_result
        
        # 3. 最后执行数据开发任务
        development_result = await self.data_developer.process_req(task)
        results["data_developer"] = development_result
        
        return results
    
    def get_agent_by_role(self, role: str):
        """Get agent instance by role"""
        agents = {
            "supervisor": self.supervisor,
            "metadata_steward": self.metadata_steward,
            "data_calibration": self.data_calibration,
            "data_developer": self.data_developer
        }
        return agents.get(role)
    
    async def execute_workflow(self, task: str) -> Dict[str, Any]:
        """Execute agents according to workflow configuration"""
        results = {}
        executed = set()
        
        async def execute_agent(role: str):
            if role in executed:
                return
            
            # 等待依赖的Agent完成
            for dep in self.workflow[role]["wait_for"]:
                if dep not in executed:
                    return
            
            # 执行Agent
            agent = self.get_agent_by_role(role)
            if agent:
                results[role] = await agent.process_task(task)
                executed.add(role)
                
                # 触发下一个Agent
                for next_role in self.workflow[role]["next"]:
                    await execute_agent(next_role)
        
        # 从 Supervisor 开始执行
        await execute_agent("supervisor")
        return results
