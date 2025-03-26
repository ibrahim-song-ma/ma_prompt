import os
import json
import httpx
from typing import Dict, Any, List, Optional, Union
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from .config import LLMConfig

class DeepSeekLLM:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.model = config.model
        # 创建OpenAI客户端
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
            http_client=httpx.AsyncClient()
        )

    async def generate(self, 
                      system_prompt: str, 
                      messages: List[Dict[str, str]], 
                      temperature: float = None) -> str:
        """使用DeepSeek API生成响应，遵循OpenAI规范"""
        try:
            # 构建消息列表
            all_messages = [
                {"role": "system", "content": system_prompt + "\nIMPORTANT: Respond with a JSON object directly, do not wrap it in markdown code blocks."}
            ] + messages

            # 调用API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=all_messages,
                temperature=temperature or self.config.temperature,
                max_tokens=self.config.max_tokens
            )

            # 获取响应内容
            content = response.choices[0].message.content
            print(f"\nLLM Response:\n{content}\n")
            
            # 移除可能的Markdown代码块
            if content.startswith('```') and content.endswith('```'):
                # 移除开始和结束的代码块标记
                content = content[content.find('\n')+1:content.rfind('```')].strip()
                # 如果还有json标记，也移除
                if content.startswith('json'):
                    content = content[4:].strip()
            
            # 返回处理后的内容
            return content

        except Exception as e:
            print(f"DeepSeek API error: {e}")
            return f"Error generating response: {str(e)}"
            
    async def tool_calling(self,
                         system_prompt: str,
                         messages: List[Dict[str, str]],
                         tools: List[Dict[str, Any]],
                         tool_choice: Optional[Dict[str, str]] = None,
                         temperature: float = None) -> Dict[str, Any]:
        """使用DeepSeek API进行工具调用，支持从工具调用或内容中提取JSON响应"""
        try:
            # 构建消息列表
            all_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages

            # 准备API调用参数
            params = {
                "model": self.model,
                "messages": all_messages,
                "temperature": temperature or self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "tools": tools
            }
            
            # 如果指定了工具选择，添加到参数中
            if tool_choice:
                params["tool_choice"] = tool_choice

            # 调用API
            print("Calling LLM with tool calling...")
            response = await self.client.chat.completions.create(**params)
            
            return await self._process_tool_calling_response(response, tools)
            
        except Exception as e:
            error_msg = f"DeepSeek function calling error: {e}"
            print(error_msg)
            return {"error": error_msg}
    
    async def _process_tool_calling_response(self, 
                                          response: ChatCompletion, 
                                          tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """处理工具调用响应，从工具调用或内容中提取JSON"""
        result = {"raw_response": response}
        
        # 获取响应消息
        message = response.choices[0].message
        result["message"] = message
        
        # 尝试从工具调用获取结果
        if message.tool_calls:
            try:
                # 获取第一个工具调用（通常只有一个）
                tool_call = message.tool_calls[0]
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                result["tool_name"] = tool_name
                result["arguments"] = arguments
                result["source"] = "tool_call"
                
                print(f"\nTool call: {tool_name}")
                print(f"Arguments: {json.dumps(arguments, indent=2, ensure_ascii=False)}")
                
                return result
                
            except json.JSONDecodeError as e:
                print(f"Error parsing tool call arguments: {e}")
                result["error"] = f"Error parsing tool call arguments: {e}"
        
        # 如果没有工具调用或解析失败，尝试从内容中提取JSON
        if message.content:
            content = message.content
            
            # 检查是否包含JSON代码块
            if '```json' in content and '```' in content.split('```json', 1)[1]:
                json_str = content.split('```json', 1)[1].split('```', 1)[0].strip()
                try:
                    # 解析JSON
                    json_data = json.loads(json_str)
                    
                    # 尝试匹配工具参数
                    matched_tool = None
                    for tool in tools:
                        # 检查JSON结构是否匹配工具参数
                        if all(key in json_data for key in tool.get("function", {}).get("parameters", {}).get("required", [])):
                            matched_tool = tool
                            break
                    
                    if matched_tool:
                        result["tool_name"] = matched_tool.get("function", {}).get("name")
                        result["arguments"] = json_data
                        result["source"] = "content_json"
                        
                        print(f"\nExtracted JSON matching tool: {matched_tool.get('function', {}).get('name')}")
                        print(f"Arguments: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                    else:
                        result["arguments"] = json_data
                        result["source"] = "content_json_unmatched"
                        
                        print("\nExtracted JSON from content (no tool match):")
                        print(json.dumps(json_data, indent=2, ensure_ascii=False))
                    
                    return result
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON from content: {e}")
                    result["error"] = f"Error parsing JSON from content: {e}"
            else:
                # 尝试直接解析整个内容为JSON
                try:
                    json_data = json.loads(content)
                    result["arguments"] = json_data
                    result["source"] = "content_direct_json"
                    
                    print("\nParsed content directly as JSON:")
                    print(json.dumps(json_data, indent=2, ensure_ascii=False))
                    
                    return result
                except json.JSONDecodeError:
                    # 不是有效的JSON，保存原始内容
                    result["content"] = content
                    result["source"] = "content_text"
        
        return result
