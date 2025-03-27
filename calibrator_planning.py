import asyncio
import json
import traceback
from typing import Dict, Any, List
from agent_system.config import load_config, AgentConfig
from agents.supervisor import SupervisorAgent
from agents.calibrator import CalibratorAgent
from agent_system.llm import DeepSeekLLM
from agent_system.message_bus import MessageBus

async def calibrator_planning():

    llm_config = load_config()
    
    supervisor_agent_config = AgentConfig(
        name="supervisor", 
        role="supervisor",
        description="Project management and task coordination",
        llm_config=llm_config
    )
    
    calibrator_agent_config = AgentConfig(
        name="calibrator", 
        role="calibrator",
        description="Data calibration and validation",
        llm_config=llm_config
    )
    llm = DeepSeekLLM(llm_config)
    message_bus = MessageBus()
    
    supervisor = SupervisorAgent(config=supervisor_agent_config, message_bus=message_bus, llm=llm)
    calibrator = CalibratorAgent(config=calibrator_agent_config, message_bus=message_bus, llm=llm)

    
    # async def handle_supervisor_message(message: Dict[str, Any]) -> None:
    #     """处理来自Supervisor的消息"""
    #     print(f"收到Supervisor消息: {message}")
    #     # 在这里添加具体的消息处理逻辑
    #     # calibrator.add_message(role="user", content=message.get("content", ""))

    # # 订阅Supervisor的消息
    # message_bus.subscribe("supervisor", handle_supervisor_message)

    # # 通过message_bus直接发布消息
    # await message_bus.publish("supervisor", {
    #     "content": "supervisor to calibrator: 需要校准数据的任务描述"
    # }, sender="supervisor")
    
    # # 给消息处理留出时间
    # await asyncio.sleep(0.1)
    
    # # 打印Calibrator收到的消息
    # print("Calibrator收到的消息:", calibrator.get_messages())
    
    return

if __name__ == "__main__":
    asyncio.run(calibrator_planning())
