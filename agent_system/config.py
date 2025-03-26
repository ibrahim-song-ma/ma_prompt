from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel
import os

class LLMConfig(BaseModel):
    """LLM configuration settings"""
    api_key: str
    model: str = "deepseek-chat"
    api_base: str = "https://api.deepseek.com/v1"
    temperature: float = 0.7
    max_tokens: int = 2000

class AgentConfig(BaseModel):
    """Base configuration for all agents"""
    name: str
    description: str
    role: str
    llm_config: LLMConfig

def load_config() -> LLMConfig:
    """Load LLM configuration from environment variables"""
    load_dotenv()
    return LLMConfig(
        api_key=os.getenv("DEEPSEEK_API_KEY", "sk-7d26badfc6c348cf8da0fc4f67eb6f85"),
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        api_base=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    )
