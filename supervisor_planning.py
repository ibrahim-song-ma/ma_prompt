import asyncio
import traceback
from agent_system.config import load_config, AgentConfig
from agents.supervisor import SupervisorAgent
from agent_system.llm import DeepSeekLLM
from agent_system.message_bus import MessageBus


async def supervisor_planning():
    llm_config = load_config()
    agent_config = AgentConfig(
        name="supervisor",
        role="supervisor",
        description="Project management and task coordination",
        llm_config=llm_config,
    )
    llm = DeepSeekLLM(llm_config)

    message_bus = MessageBus()

    supervisor = SupervisorAgent(config=agent_config, message_bus=message_bus, llm=llm)
    req = """支撑省内集团客户部对外大数据服务合作项目，需要用户行业网关短信收发时间明细数据的支撑。需包含集团客户名称，行业子类型名称，服务代码，第三方电话，短信发送状态，处理结束日期，处理结束时间，统计日期等信息。"""

    print("Processing task with SupervisorAgent...")
    try:
        result = await supervisor.process_req(req)
        return supervisor.handle_req_process_result(result)
    except Exception as e:
        print(f"\nException occurred: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        return result


if __name__ == "__main__":
    asyncio.run(supervisor_planning())
