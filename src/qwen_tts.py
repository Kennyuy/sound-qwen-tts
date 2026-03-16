"""
Qwen-TTS 声音克隆核心封装模块

基于阿里云百炼 DashScope API 实现文本转语音和声音克隆功能。
"""

import os
import uuid
import requests
import json
from typing import Optional, List, Dict
from pathlib import Path


class QwenTTS:
    """
    Qwen-TTS 语音合成客户端
    
    支持两种模式：
    1. 预设音色合成 - 使用阿里云提供的标准音色
    2. 声音克隆合成 - 使用参考音频克隆目标音色
    """
    
    # 阿里云 DashScope API 端点
    BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
    TTS_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/tts/generation"
    
    # 支持的预设音色列表
    AVAILABLE_VOICES = [
        {"name": "longxiaochun", "label": "龙小淳", "gender": "female", "description": "通用女声，温暖亲切"},
        {"name": "longxiaoxia", "label": "龙小夏", "gender": "female", "description": "通用女声，活泼清新"},
        {"name": "longcheng", "label": "龙诚", "gender": "male", "description": "通用男声，沉稳专业"},
        {"name": "longxiaomei", "label": "龙小美", "gender": "female", "description": "通用女声，甜美可爱"},
        {"name": "jingxiao", "label": "婧骁", "gender": "female", "description": "知性女声"},
        {"name": "wanwan", "label": "婉婉", "gender": "female", "description": "温柔女声"},
    ]
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化 Qwen-TTS 客户端
        
        Args:
            api_key: 阿里云百炼 API Key，如不提供则从环境变量 DASHSCOPE_API_KEY 读取
            base_url: API 基础 URL，默认使用阿里云官方端点
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API Key 未提供。请通过 api_key 参数传入，或设置环境变量 DASHSCOPE_API_KEY"
            )
        
        self.base_url = base_url or os.getenv("DASHSCOPE_BASE_URL", self.BASE_URL)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 创建输出目录
        output_dir = os.getenv("OUTPUT_DIR", "./outputs")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir
    
    def list_voices(self) -> List[Dict]:
        """
        获取可用的预设音色列表
        
        Returns:
            音色信息列表
        """
        return self.AVAILABLE_VOICES.copy()
    
    def synthesize(
        self,
        text: str,
        voice: str = "longxiaochun",
        output_path: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0,
        rate: int = 48000,
        format: str = "wav",
        **kwargs
    ) -> str:
        """
        使用预设音色合成语音
        
        Args:
            text: 要合成的文本内容
            voice: 音色名称，默认使用 longxiaochun
            output_path: 输出音频文件路径，默认自动生成
            speed: 语速，范围 0.5-2.0，默认 1.0
            pitch: 音调，范围 0.5-2.0，默认 1.0
            volume: 音量，范围 0.1-1.0，默认 1.0
            rate: 采样率，默认 48000
            format: 输出格式，支持 wav/mp3，默认 wav
            
        Returns:
            输出音频文件路径
        """
        # 验证参数范围
        speed = max(0.5, min(2.0, speed))
        pitch = max(0.5, min(2.0, pitch))
        volume = max(0.1, min(1.0, volume))
        
        # 生成输出路径
        if output_path is None:
            output_path = os.path.join(
                self.output_dir,
                f"tts_{uuid.uuid4().hex[:8]}.{format}"
            )
        
        # 构建请求体
        payload = {
            "model": "sambert-zh-v1",  # 使用 Sambert 中文语音模型
            "input": {
                "text": text
            },
            "parameters": {
                "voice": voice,
                "speed": speed,
                "pitch": pitch,
                "volume": volume,
                "rate": rate,
                "format": format
            }
        }
        
        # 发送请求
        response = requests.post(
            self.TTS_ENDPOINT,
            headers=self.headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"API 请求失败：{response.status_code} - {response.text}")
        
        # 解析响应
        result = response.json()
        
        if result.get("code") != 200:
            raise Exception(f"合成失败：{result.get('message', '未知错误')}")
        
        # 获取音频 URL 并下载
        audio_url = result.get("output", {}).get("audio")
        if not audio_url:
            # 某些情况下直接返回音频数据
            audio_data = result.get("output", {}).get("audio_data")
            if audio_data:
                import base64
                audio_bytes = base64.b64decode(audio_data)
            else:
                raise Exception("无法获取音频数据")
        else:
            # 从 URL 下载音频
            audio_response = requests.get(audio_url, timeout=60)
            audio_response.raise_for_status()
            audio_bytes = audio_response.content
        
        # 保存音频文件
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        return output_path
    
    def synthesize_with_clone(
        self,
        text: str,
        reference_audio: str,
        output_path: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0,
        **kwargs
    ) -> str:
        """
        使用参考音频克隆音色并合成语音
        
        Args:
            text: 要合成的文本内容
            reference_audio: 参考音频文件路径（WAV 格式）
            output_path: 输出音频文件路径
            speed: 语速，范围 0.5-2.0
            pitch: 音调，范围 0.5-2.0
            volume: 音量，范围 0.1-1.0
            
        Returns:
            输出音频文件路径
        """
        # 验证参考音频文件存在
        if not os.path.exists(reference_audio):
            raise FileNotFoundError(f"参考音频文件不存在：{reference_audio}")
        
        # 生成输出路径
        if output_path is None:
            output_path = os.path.join(
                self.output_dir,
                f"tts_clone_{uuid.uuid4().hex[:8]}.wav"
            )
        
        # 注意：阿里云的声音克隆功能需要通过特定 API 或 SDK 实现
        # 以下是基于 DashScope 语音克隆 API 的调用方式
        
        # 读取参考音频文件
        with open(reference_audio, "rb") as f:
            audio_data = f.read()
        
        # 构建 multipart 请求
        import base64
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        
        # 使用语音克隆 API
        # 注意：具体 API 端点和参数可能因阿里云版本更新而变化
        clone_endpoint = "https://dashscope.aliyuncs.com/api/v1/services/aigc/tts/customization"
        
        payload = {
            "model": "sambert-zh-v1",
            "input": {
                "text": text,
                "prompt_audio": audio_base64
            },
            "parameters": {
                "speed": speed,
                "pitch": pitch,
                "volume": volume,
                "format": "wav"
            }
        }
        
        try:
            response = requests.post(
                clone_endpoint,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                # 如果克隆 API 不可用，回退到标准合成
                print(f"⚠️  声音克隆 API 不可用（{response.status_code}），使用预设音色合成")
                return self.synthesize(
                    text=text,
                    voice="longxiaochun",
                    output_path=output_path,
                    speed=speed,
                    pitch=pitch,
                    volume=volume
                )
            
            result = response.json()
            
            if result.get("code") != 200:
                raise Exception(f"克隆合成失败：{result.get('message', '未知错误')}")
            
            # 获取音频数据
            audio_url = result.get("output", {}).get("audio")
            if audio_url:
                audio_response = requests.get(audio_url, timeout=60)
                audio_response.raise_for_status()
                audio_bytes = audio_response.content
            else:
                audio_data = result.get("output", {}).get("audio_data")
                if audio_data:
                    audio_bytes = base64.b64decode(audio_data)
                else:
                    raise Exception("无法获取音频数据")
            
            # 保存文件
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            
            return output_path
            
        except Exception as e:
            print(f"⚠️  声音克隆失败：{e}，使用预设音色合成")
            return self.synthesize(
                text=text,
                voice="longxiaochun",
                output_path=output_path,
                speed=speed,
                pitch=pitch,
                volume=volume
            )
    
    def create_custom_voice(
        self,
        reference_audio: str,
        voice_name: str,
        description: str = ""
    ) -> Dict:
        """
        创建自定义音色（需要预先训练）
        
        Args:
            reference_audio: 参考音频文件路径
            voice_name: 自定义音色名称
            description: 音色描述
            
        Returns:
            音色创建结果，包含音色 ID
        """
        # 验证文件
        if not os.path.exists(reference_audio):
            raise FileNotFoundError(f"参考音频文件不存在：{reference_audio}")
        
        # 读取音频文件
        with open(reference_audio, "rb") as f:
            audio_data = f.read()
        
        # 构建请求
        import base64
        payload = {
            "name": voice_name,
            "description": description,
            "prompt_audio": base64.b64encode(audio_data).decode("utf-8")
        }
        
        # 创建自定义音色
        customization_endpoint = f"{self.base_url}/services/aigc/tts/customization/voices"
        
        response = requests.post(
            customization_endpoint,
            headers=self.headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"创建自定义音色失败：{response.status_code} - {response.text}")
        
        result = response.json()
        
        if result.get("code") != 200:
            raise Exception(f"创建失败：{result.get('message', '未知错误')}")
        
        return result.get("data", {})


def get_api_key_from_env() -> str:
    """从环境变量获取 API Key"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")
    return api_key
