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

    req = """支撑省内集团客户部对外大数据服务合作项目，需要用户行业网关短信收发时间明细数据的支撑。需包含集团客户名称，行业子类型名称，服务代码，第三方电话，短信发送状态，处理结束日期，处理结束时间，统计日期等信息。"""

    print(f"Processing task with SupervisorAgent & CalibratorAgent...")
    try:
        supervisor_result = await supervisor.process_req(req)
        supervisor_result = supervisor.handle_plan_result(supervisor_result)
        msg_for_calbrator = supervisor.prepare_calibrator_msg(supervisor_result)
        print("SupervisorAgent processed results, passing to calibrator:", msg_for_calbrator)
        
        msg_for_calibrator_str = json.dumps(msg_for_calbrator, ensure_ascii=False, indent=2)
        calibrator_result = await calibrator.process_req(msg_for_calibrator_str)
        calibrator_result = calibrator.handle_plan_result(calibrator_result)
        # print("CalibratorAgent处理结果:", calibrator_result)
        return calibrator_result
    except Exception as e:      
        print(f"\nException occurred: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        return msg_for_calbrator

if __name__ == "__main__":
    asyncio.run(calibrator_planning())
