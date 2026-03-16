"""
Qwen-TTS 声音克隆包

基于阿里云百炼 DashScope API 实现文本转语音和声音克隆功能。
"""

from .qwen_tts import QwenTTS, get_api_key_from_env

__version__ = "1.0.0"
__author__ = "Kenny"
__all__ = ["QwenTTS", "get_api_key_from_env"]
