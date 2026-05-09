#!/usr/bin/env python3
"""
统一LLM调用封装，支持多个大模型供应商
支持: Doubao (OpenAI-compatible), Anthropic Claude
"""

import os
import json
import base64
from typing import Optional
from dotenv import load_dotenv


class LLMClient:
    """统一的LLM客户端，根据配置自动选择Provider"""

    def __init__(self):
        load_dotenv()
        self.provider = os.getenv("LLM_PROVIDER", "doubao").lower()
        self.api_key = os.getenv("LLM_API_KEY")
        self.model = os.getenv("LLM_MODEL", "doubao-1-5-vision-pro-32k-250115")
        self.base_url = os.getenv("LLM_BASE_URL", "https://ark.volces.com/api/v3")

        if not self.api_key:
            raise ValueError("LLM_API_KEY not found in environment")

    def chat_with_image(self, system_prompt: str, user_prompt: str, image_b64: str) -> str:
        """
        统一接口：调用大模型处理图像+文本
        返回模型的文本响应
        """
        if self.provider == "doubao":
            return self._chat_with_image_openai(system_prompt, user_prompt, image_b64)
        elif self.provider == "anthropic":
            return self._chat_with_image_anthropic(system_prompt, user_prompt, image_b64)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def chat(self, message: str) -> str:
        """纯文本消息，无图像"""
        if self.provider == "doubao":
            return self._chat_openai(message)
        elif self.provider == "anthropic":
            return self._chat_anthropic(message)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _chat_with_image_openai(self, system_prompt: str, user_prompt: str, image_b64: str) -> str:
        """使用豆包ARK API处理图像"""
        import requests

        # 使用豆包原生 API 格式
        url = f"{self.base_url.rstrip('/responses')}/responses"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{image_b64}"
                        },
                        {
                            "type": "input_text",
                            "text": f"{system_prompt}\n\n{user_prompt}"
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()

        # 豆包 API 响应格式: output 是数组，每个元素可能是 reasoning 或 message
        if "output" in data and len(data["output"]) > 0:
            for item in data["output"]:
                if item.get("type") == "message" and "content" in item:
                    for content in item["content"]:
                        if content.get("type") == "output_text":
                            return content.get("text", "")
        raise ValueError(f"No text response in output: {data}")

    def _chat_with_image_anthropic(self, system_prompt: str, user_prompt: str, image_b64: str) -> str:
        """使用Anthropic Claude处理图像"""
        from anthropic import Anthropic

        client = Anthropic(api_key=self.api_key)

        message = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": user_prompt},
                    ],
                }
            ],
        )

        return message.content[0].text

    def _chat_openai(self, message: str) -> str:
        """使用豆包ARK API处理纯文本"""
        import requests

        url = f"{self.base_url.rstrip('/responses')}/responses"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": message
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()

        # 豆包 API 响应格式: output 是数组，每个元素可能是 reasoning 或 message
        if "output" in data and len(data["output"]) > 0:
            for item in data["output"]:
                if item.get("type") == "message" and "content" in item:
                    for content in item["content"]:
                        if content.get("type") == "output_text":
                            return content.get("text", "")
        raise ValueError(f"No text response in output: {data}")

    def _chat_anthropic(self, message: str) -> str:
        """Anthropic Claude纯文本消息"""
        from anthropic import Anthropic

        client = Anthropic(api_key=self.api_key)

        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2000,
            messages=[{"role": "user", "content": message}],
        )

        return response.content[0].text
