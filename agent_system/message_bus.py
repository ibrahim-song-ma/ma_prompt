from typing import Dict, Any, List, Callable
import asyncio
from collections import defaultdict

class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_history: List[Dict[str, Any]] = []

    def subscribe(self, topic: str, callback: Callable):
        """订阅特定主题"""
        self.subscribers[topic].append(callback)

    def unsubscribe(self, topic: str, callback: Callable):
        """取消订阅"""
        if topic in self.subscribers:
            self.subscribers[topic].remove(callback)

    async def publish(self, topic: str, message: Dict[str, Any], sender: str = None):
        """发布消息到特定主题"""
        message_with_metadata = {
            "topic": topic,
            "content": message,
            "sender": sender,
            "timestamp": asyncio.get_event_loop().time()
        }
        self.message_history.append(message_with_metadata)
        
        tasks = []
        for callback in self.subscribers[topic]:
            tasks.append(asyncio.create_task(callback(message_with_metadata)))
        
        if tasks:
            await asyncio.gather(*tasks)

    def get_message_history(self, topic: str = None) -> List[Dict[str, Any]]:
        """获取消息历史"""
        if topic:
            return [msg for msg in self.message_history if msg["topic"] == topic]
        return self.message_history
