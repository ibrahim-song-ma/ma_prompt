import asyncio
import json
import logging
from typing import Dict, List, Any
from pydantic import BaseModel
from agent_system.agent_system import AgentSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskPlan(BaseModel):
    steps: List[Dict[str, str]]
    assigned_agents: List[str]


def get_task_plan() -> Dict[str, Any]:
    """Function that will be available to LLM for planning tasks"""
    return {
        "name": "get_task_plan",
        "description": "Plan the execution steps and assign agents",
        "parameters": TaskPlan.model_json_schema(),
    }


def assign_tasks(plan: Dict[str, Any]) -> str:
    """Distribute tasks to agents according to the plan"""
    return f"Tasks assigned according to plan: {json.dumps(plan, indent=2)}"


async def test_supervisor_planning():
    try:
        # Initialize the agent system
        logger.info("Initializing agent system...")
        agent_system = AgentSystem()
        logger.info("Agent system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent system: {e}")
        raise

    # Define system message with agent knowledge
    system_message = """You are a Supervisor Agent responsible for planning and coordinating tasks.
    Available Agents and their responsibilities:
    1. Supervisor Agent (You): Project management and task coordination
    2. Metadata Steward: Data governance and metadata management
    3. Data Calibration: Data quality and validation
    4. Data Developer: Data pipeline development and maintenance

    When given a task, create a detailed plan and assign appropriate agents.
    Return your response as a JSON object with two fields:
    1. steps: List of dictionaries containing step descriptions and their owners
    2. assigned_agents: List of agent names that will be involved
    """

    # Your test prompt
    user_prompt = """Create a data pipeline that:
    1. Ingests customer transaction data
    2. Validates data quality
    3. Transforms it for analysis
    4. Stores it in our data warehouse"""

    try:
        # Call LLM with function calling
        logger.info("Calling LLM with function calling...")
        response = await agent_system.llm.generate(
            system_prompt=system_message,
            messages=[{"role": "user", "content": user_prompt}],
        )
        logger.info(f"Received response from LLM: {response}")
    except Exception as e:
        logger.error(f"Failed to generate response from LLM: {e}")
        raise

    # Parse the response as JSON
    try:
        plan = json.loads(response)
        result = assign_tasks(plan)
        print(result)
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Raw response: {response}")


if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_supervisor_planning())
