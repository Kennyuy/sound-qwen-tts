#!/usr/bin/env python3
"""
Qwen-TTS 命令行客户端

使用方法:
    # 使用预设音色合成
    python tts_client.py --text "你好世界" --output output.wav
    
    # 使用声音克隆
    python tts_client.py --text "你好世界" --reference wtw.WAV --output cloned.wav
    
    # 调整参数
    python tts_client.py --text "你好世界" --speed 1.2 --pitch 0.9
"""

import argparse
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.qwen_tts import QwenTTS, get_api_key_from_env


def main():
    parser = argparse.ArgumentParser(
        description="Qwen-TTS 语音合成命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用预设音色合成
  %(prog)s --text "你好，这是测试语音" --output test.wav
  
  # 使用声音克隆
  %(prog)s --text "你好" --reference samples/wtw.WAV --output cloned.wav
  
  # 调整语速和音调
  %(prog)s --text "你好" --speed 1.2 --pitch 0.9
  
  # 列出可用音色
  %(prog)s --list-voices
        """
    )
    
    # 输入参数
    parser.add_argument(
        "--text", "-t",
        type=str,
        help="要合成的文本内容"
    )
    
    parser.add_argument(
        "--reference", "-r",
        type=str,
        help="参考音频文件路径（用于声音克隆）"
    )
    
    # 输出参数
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output.wav",
        help="输出音频文件路径（默认：output.wav）"
    )
    
    # 音色参数
    parser.add_argument(
        "--voice", "-v",
        type=str,
        default="longxiaochun",
        help="预设音色名称（默认：longxiaochun）"
    )
    
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="列出所有可用音色"
    )
    
    # 语音参数
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="语速，范围 0.5-2.0（默认：1.0）"
    )
    
    parser.add_argument(
        "--pitch",
        type=float,
        default=1.0,
        help="音调，范围 0.5-2.0（默认：1.0）"
    )
    
    parser.add_argument(
        "--volume",
        type=float,
        default=1.0,
        help="音量，范围 0.1-1.0（默认：1.0）"
    )
    
    # 其他参数
    parser.add_argument(
        "--api-key",
        type=str,
        help="阿里云百炼 API Key（也可通过环境变量 DASHSCOPE_API_KEY 设置）"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细输出"
    )
    
    args = parser.parse_args()
    
    # 列出音色模式
    if args.list_voices:
        list_voices()
        return
    
    # 验证必要参数
    if not args.text:
        parser.error("请提供要合成的文本内容 (--text)")
    
    # 初始化客户端
    try:
        api_key = args.api_key or get_api_key_from_env()
        tts = QwenTTS(api_key=api_key)
    except ValueError as e:
        print(f"❌ 错误：{e}")
        print("\n请设置环境变量 DASHSCOPE_API_KEY 或使用 --api-key 参数")
        sys.exit(1)
    
    # 执行合成
    try:
        if args.reference:
            # 声音克隆模式
            if args.verbose:
                print(f"🎤 使用声音克隆模式")
                print(f"   参考音频：{args.reference}")
            
            output_path = tts.synthesize_with_clone(
                text=args.text,
                reference_audio=args.reference,
                output_path=args.output,
                speed=args.speed,
                pitch=args.pitch,
                volume=args.volume
            )
        else:
            # 预设音色模式
            if args.verbose:
                print(f"🎵 使用预设音色：{args.voice}")
            
            output_path = tts.synthesize(
                text=args.text,
                voice=args.voice,
                output_path=args.output,
                speed=args.speed,
                pitch=args.pitch,
                volume=args.volume
            )
        
        print(f"✅ 合成完成！")
        print(f"   输出文件：{output_path}")
        
    except Exception as e:
        print(f"❌ 合成失败：{e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def list_voices():
    """列出所有可用音色"""
    tts = QwenTTS.__new__(QwenTTS)  # 不需要初始化即可访问类属性
    voices = tts.AVAILABLE_VOICES
    
    print("\n🎵 可用音色列表:\n")
    print(f"{'名称':<20} {'性别':<8} {'描述':<30}")
    print("-" * 60)
    
    for voice in voices:
        gender = "女声" if voice["gender"] == "female" else "男声"
        print(f"{voice['name']:<20} {gender:<8} {voice['description']:<30}")
    
    print("\n💡 使用 --voice <名称> 选择音色")
    print("   例如：--voice longxiaochun\n")


if __name__ == "__main__":
    main()
