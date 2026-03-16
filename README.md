# Sound-Qwen-TTS

基于阿里云百炼 (DashScope) Qwen-TTS 模型的声音克隆项目。

## 项目简介

本项目使用阿里云百炼平台的 Qwen-TTS 模型，通过参考音频文件实现声音克隆功能。用户上传一段参考音频，系统可以提取音色特征，并使用该音色合成任意文本的语音。

## 功能特性

- 🎤 **声音克隆** - 使用参考音频克隆目标音色
- 📝 **文本转语音** - 将任意文本转换为自然流畅的语音
- 🔧 **灵活配置** - 支持多种语音参数调整（语速、音调、音量等）
- 📦 **简单易用** - 提供命令行和 Python API 两种使用方式

## 环境要求

- Python 3.8+
- 阿里云百炼 API Key
- 参考音频文件（WAV 格式，建议 16bit/44100Hz）

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/Kennyuy/sound-qwen-tts.git
cd sound-qwen-tts
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

复制配置文件模板并填入你的 API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的阿里云百炼 API Key：

```
DASHSCOPE_API_KEY=sk-your-api-key-here
```

## 使用方法

### 方式一：命令行使用

#### 声音克隆 + 语音合成

```bash
python src/tts_client.py \
  --reference wtw.WAV \
  --text "你好，这是使用声音克隆技术生成的语音。" \
  --output output.wav
```

#### 使用预设音色（不克隆）

```bash
python src/tts_client.py \
  --text "你好，这是使用预设音色生成的语音。" \
  --voice longxiaochun \
  --output output.wav
```

### 方式二：Python API

```python
from src.qwen_tts import QwenTTS

# 初始化客户端
tts = QwenTTS(api_key="sk-your-api-key")

# 声音克隆模式
audio_path = tts.synthesize_with_clone(
    text="你好，这是使用声音克隆技术生成的语音。",
    reference_audio="wtw.WAV",
    output_path="output.wav"
)

# 或者使用预设音色
audio_path = tts.synthesize(
    text="你好，这是使用预设音色生成的语音。",
    voice="longxiaochun",
    output_path="output.wav"
)
```

### 方式三：交互模式

```bash
python src/interactive.py
```

## 参数说明

### 语音合成参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `text` | str | 必填 | 要合成的文本内容 |
| `voice` | str | longxiaochun | 音色名称（克隆模式下可忽略） |
| `reference_audio` | str | 可选 | 参考音频文件路径（克隆模式必填） |
| `output_path` | str | output.wav | 输出音频文件路径 |
| `speed` | float | 1.0 | 语速（0.5-2.0） |
| `pitch` | float | 1.0 | 音调（0.5-2.0） |
| `volume` | float | 1.0 | 音量（0.1-1.0） |

### 支持的预设音色

- `longxiaochun` - 龙小淳（通用女声）
- `longxiaoxia` - 龙小夏（通用女声）
- `longcheng` - 龙诚（通用男声）
- `longxiaomei` - 龙小美（通用女声）
- `star` - 明星音色（需额外权限）

## 项目结构

```
sound-qwen-tts/
├── README.md              # 项目说明文档
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量模板
├── .gitignore            # Git 忽略配置
├── src/
│   ├── __init__.py       # 包初始化
│   ├── qwen_tts.py       # Qwen-TTS 核心封装
│   ├── tts_client.py     # 命令行客户端
│   └── interactive.py    # 交互式界面
├── samples/
│   └── wtw.WAV           # 示例参考音频
└── outputs/              # 合成输出目录（自动创建）
```

## API 参考

### QwenTTS 类

```python
class QwenTTS:
    def __init__(self, api_key: str, base_url: str = None)
    
    def synthesize(self, text: str, voice: str = "longxiaochun", 
                   output_path: str = "output.wav", **kwargs) -> str
        """使用预设音色合成语音"""
    
    def synthesize_with_clone(self, text: str, reference_audio: str,
                              output_path: str = "output.wav", **kwargs) -> str
        """使用参考音频克隆音色并合成语音"""
    
    def list_voices(self) -> List[Dict]
        """获取可用音色列表"""
```

## 注意事项

1. **音频格式**：参考音频建议使用 WAV 格式，16bit/44100Hz，时长 10-60 秒
2. **API 配额**：请查看阿里云百炼控制台的配额限制
3. **网络要求**：需要稳定的网络连接以访问阿里云 API
4. **音色质量**：参考音频的清晰度直接影响克隆效果

## 常见问题

### Q: 声音克隆效果不理想怎么办？

A: 尝试以下方法：
- 使用更清晰的参考音频（无背景噪音）
- 参考音频时长建议在 30 秒以上
- 调整语速、音调等参数

### Q: 如何获取 API Key？

A: 访问 [阿里云百炼控制台](https://bailian.console.aliyun.com/)，在 API 管理页面创建并获取 API Key。

### Q: 支持哪些音频格式输出？

A: 默认输出 WAV 格式，可通过修改代码支持 MP3 等其他格式。

## 许可证

MIT License

## 作者

Kenny

## 更新日志

- 2026-03-16: 初始版本，支持基本的声音克隆功能
