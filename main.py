import asyncio
from agent_system import AgentSystem


async def run_task(system: AgentSystem, task: str):
    """Run a task through the agent system"""
    print(f"Processing task: {task}")

    print("\nExecuting standard workflow:")
    result = await system.process_task(task)
    print_results(system, result)

    print("\nExecuting custom workflow:")
    workflow_result = await system.execute_workflow(task)
    print_results(system, workflow_result)


def print_results(system: AgentSystem, results: dict):
    """Print execution results"""
    print("\nExecution Results:")
    print("=================\n")

    for agent, result in results.items():
        print(f"Agent: {agent.title()}")
        print("Messages:")

        # 获取Agent的消息历史
        agent_instance = system.get_agent_by_role(agent)
        if agent_instance:
            for msg in agent_instance.get_messages():
                sender = msg.get("sender", "unknown")
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                print(f"[{sender}] ({role}): {content}")

        print("\nFinal Result:")
        print(result)
        print("-" * 80)
        print()


async def main():
    print("Starting Agent System test...")

    # 初始化Agent系统
    system = AgentSystem()

    # 测试任务
    test_task = "分析销售数据，生成每月销售报表"

    # 执行任务
    await run_task(system, test_task)


if __name__ == "__main__":
    asyncio.run(main())
