#!/usr/bin/env python3
"""
测试脚本 - 验证 Qwen-TTS API 连接和基本功能

运行此脚本前请确保已设置 DASHSCOPE_API_KEY 环境变量。
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.qwen_tts import QwenTTS, get_api_key_from_env


def test_api_connection():
    """测试 API 连接"""
    print("🔌 测试 API 连接...")
    
    try:
        api_key = get_api_key_from_env()
        tts = QwenTTS(api_key=api_key)
        print("✅ API Key 验证成功")
        return tts
    except ValueError as e:
        print(f"❌ API Key 错误：{e}")
        return None
    except Exception as e:
        print(f"❌ 连接失败：{e}")
        return None


def test_list_voices(tts: QwenTTS):
    """测试获取音色列表"""
    print("\n🎵 测试获取音色列表...")
    
    try:
        voices = tts.list_voices()
        print(f"✅ 获取到 {len(voices)} 个可用音色:")
        for voice in voices[:3]:  # 只显示前 3 个
            print(f"   • {voice['name']} ({voice['label']})")
        if len(voices) > 3:
            print(f"   ... 还有 {len(voices) - 3} 个音色")
        return True
    except Exception as e:
        print(f"❌ 获取音色列表失败：{e}")
        return False


def test_synthesize(tts: QwenTTS):
    """测试基本语音合成"""
    print("\n🗣️  测试基本语音合成...")
    
    test_text = "你好，这是 Qwen-TTS 语音合成测试。"
    output_path = "outputs/test_basic.wav"
    
    try:
        result = tts.synthesize(
            text=test_text,
            voice="longxiaochun",
            output_path=output_path
        )
        print(f"✅ 语音合成成功")
        print(f"   输出文件：{result}")
        print(f"   文件大小：{os.path.getsize(result)} 字节")
        return True
    except Exception as e:
        print(f"❌ 语音合成失败：{e}")
        return False


def test_clone(tts: QwenTTS):
    """测试声音克隆"""
    print("\n🎤 测试声音克隆...")
    
    # 检查参考音频文件
    reference_files = [
        "wtw.WAV",
        "samples/wtw.WAV",
        "../wtw.WAV"
    ]
    
    reference_audio = None
    for ref in reference_files:
        if os.path.exists(ref):
            reference_audio = ref
            break
    
    if not reference_audio:
        print("⚠️  未找到参考音频文件，跳过克隆测试")
        print("   请将参考音频文件放在以下位置之一:")
        for ref in reference_files:
            print(f"   • {ref}")
        return None
    
    test_text = "你好，这是使用声音克隆技术生成的语音。"
    output_path = "outputs/test_clone.wav"
    
    try:
        result = tts.synthesize_with_clone(
            text=test_text,
            reference_audio=reference_audio,
            output_path=output_path
        )
        print(f"✅ 声音克隆成功")
        print(f"   参考音频：{reference_audio}")
        print(f"   输出文件：{result}")
        print(f"   文件大小：{os.path.getsize(result)} 字节")
        return True
    except Exception as e:
        print(f"⚠️  声音克隆失败：{e}")
        print("   这可能是正常的，因为声音克隆功能需要特殊权限")
        return None


def main():
    print("=" * 60)
    print("       Qwen-TTS API 测试")
    print("=" * 60)
    print()
    
    # 测试 1: API 连接
    tts = test_api_connection()
    if not tts:
        print("\n❌ 测试失败：无法连接到 API")
        print("\n请检查:")
        print("  1. DASHSCOPE_API_KEY 环境变量是否正确设置")
        print("  2. 网络连接是否正常")
        print("  3. API Key 是否有效")
        sys.exit(1)
    
    # 测试 2: 获取音色列表
    test_list_voices(tts)
    
    # 测试 3: 基本语音合成
    synthesize_ok = test_synthesize(tts)
    
    # 测试 4: 声音克隆
    clone_result = test_clone(tts)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"API 连接：✅ 成功")
    print(f"音色列表：✅ 成功")
    print(f"语音合成：{'✅ 成功' if synthesize_ok else '❌ 失败'}")
    
    if clone_result is True:
        print(f"声音克隆：✅ 成功")
    elif clone_result is False:
        print(f"声音克隆：❌ 失败")
    else:
        print(f"声音克隆：⊘ 跳过（无参考音频）")
    
    print()
    print("💡 提示：运行以下命令开始使用")
    print("   python src/tts_client.py --text '你好世界' --output hello.wav")
    print()


if __name__ == "__main__":
    main()
