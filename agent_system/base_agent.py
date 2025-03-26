from typing import Dict, Any, List, Optional
from .config import AgentConfig
from .llm import DeepSeekLLM
from .message_bus import MessageBus
import asyncio
import json
import traceback

class BaseAgent:
    def __init__(self, config: AgentConfig, message_bus: MessageBus, llm: Optional[DeepSeekLLM] = None):
        self.config = config
        self.context = {}
        self.messages = []
        self.message_bus = message_bus
        self.llm = llm
        
        # 订阅与当前Agent角色相关的消息
        self.message_bus.subscribe(self.config.role, self.handle_message)
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        """处理任务并返回结果
        默认实现使用普通的LLM生成方式，子类可以重写此方法使用工具调用功能
        """
        # 添加任务到消息历史
        self.add_message("user", task)
        
        # 使用LLM生成响应
        if self.llm:
            response = await self.llm.generate(
                system_prompt=self.get_system_prompt(),
                messages=self.messages
            )
            
            try:
                # 尝试解析LLM响应为结构化数据
                result = json.loads(response)
            except json.JSONDecodeError:
                # 如果无法解析为JSON，返回原始响应
                result = {"response": response}
            
            # 添加LLM响应到消息历史
            self.add_message("assistant", str(result))
            
            # 发布结果到消息总线
            await self.publish_result(result)
            
            return result
        else:
            raise NotImplementedError("LLM not configured for this agent")
            
    async def process_task_with_tool_calling(self, 
                                           task: str, 
                                           tools: List[Dict[str, Any]], 
                                           tool_choice: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """使用工具调用处理任务并返回结果"""
        # 添加任务到消息历史
        self.add_message("user", task)
        
        # 使用LLM工具调用生成响应
        if self.llm:
            print(f"\nCalling LLM with tools: {json.dumps(tools, indent=2)}")
            print(f"Tool choice: {tool_choice}")
            
            try:
                response_data = await self.llm.tool_calling(
                    system_prompt=self.get_system_prompt(),
                    messages=self.messages,
                    tools=tools,
                    tool_choice=tool_choice
                )

                # 检查响应是否有效
                if "error" in response_data:
                    raise ValueError(response_data["error"])

                result = {"status": "success"}

                # 处理工具调用
                if "tool_name" in response_data and "arguments" in response_data:
                    result.update({
                        "tool_name": response_data["tool_name"],
                        "arguments": response_data["arguments"],
                        "source": response_data.get("source", "tool_call")
                    })

                    print(f"\nTool call: {response_data['tool_name']}")
                    print(f"Arguments: {json.dumps(response_data['arguments'], indent=2, ensure_ascii=False)}")

                # 添加LLM响应到消息历史
                self.add_message("assistant", str(result))
                
                # 发布结果到消息总线
                await self.publish_result(result)
                
                return result

            except Exception as e:
                result = {
                    "error": f"Exception during tool calling: {str(e)}",
                    "status": "error",
                    "stack_trace": traceback.format_exc()
                }
            
            # 添加LLM响应到消息历史
            self.add_message("assistant", str(result))
            
            # 发布结果到消息总线
            await self.publish_result(result)
            
            return result
        else:
            raise NotImplementedError("LLM not configured for this agent")
    
    def get_system_prompt(self) -> str:
        """获取Agent的系统提示词"""
        raise NotImplementedError
    
    async def handle_message(self, message: Dict[str, Any]):
        """处理从消息总线接收到的消息"""
        # 默认实现：将消息添加到上下文
        self.context.update(message)
    
    async def publish_result(self, result: Dict[str, Any]):
        """发布结果到消息总线"""
        await self.message_bus.publish(
            topic=f"{self.config.role}_result",
            message=result,
            sender=self.config.role
        )
    
    def add_message(self, role: str, content: str):
        """添加消息到对话历史"""
        self.messages.append({
            "role": role, 
            "content": content,
            "sender": self.config.role if role == "assistant" else "user"
        })
    
    def get_messages(self) -> List[Dict[str, str]]:
        """获取所有对话历史"""
        return self.messages
    
    def clear_messages(self):
        """清空对话历史"""
        self.messages = []
