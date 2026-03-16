#!/usr/bin/env python3
"""
Qwen-TTS 交互式界面

提供简单的命令行交互界面，方便快速测试语音合成功能。
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.qwen_tts import QwenTTS, get_api_key_from_env


def print_banner():
    """打印欢迎横幅"""
    print("\n" + "=" * 60)
    print("       🎤  Qwen-TTS 声音克隆交互式界面  🎤")
    print("=" * 60)
    print()
    print("命令说明:")
    print("  [文本]     - 直接输入文本进行合成")
    print("  /voice     - 切换音色")
    print("  /clone     - 切换到声音克隆模式")
    print("  /speed     - 调整语速")
    print("  /pitch     - 调整音调")
    print("  /volume    - 调整音量")
    print("  /voices    - 查看可用音色")
    print("  /help      - 显示帮助")
    print("  /quit      - 退出程序")
    print()
    print("-" * 60)


def print_settings(voice, speed, pitch, volume, clone_mode, reference):
    """打印当前设置"""
    print(f"\n📋 当前设置:")
    print(f"   模式：{'声音克隆' if clone_mode else '预设音色'}")
    if clone_mode:
        print(f"   参考音频：{reference or '未设置'}")
    else:
        print(f"   音色：{voice}")
    print(f"   语速：{speed}x")
    print(f"   音调：{pitch}x")
    print(f"   音量：{volume*100:.0f}%")
    print()


def main():
    # 初始化
    try:
        api_key = get_api_key_from_env()
        tts = QwenTTS(api_key=api_key)
    except ValueError as e:
        print(f"❌ 错误：{e}")
        print("\n请设置环境变量 DASHSCOPE_API_KEY")
        print("方法：export DASHSCOPE_API_KEY=sk-your-key")
        sys.exit(1)
    
    # 默认设置
    voice = "longxiaochun"
    speed = 1.0
    pitch = 1.0
    volume = 1.0
    clone_mode = False
    reference_audio = None
    
    print_banner()
    print_settings(voice, speed, pitch, volume, clone_mode, reference_audio)
    
    # 交互循环
    counter = 0
    
    while True:
        try:
            user_input = input("🎤 请输入文本或命令：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见！")
            break
        
        if not user_input:
            continue
        
        # 处理命令
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else None
            
            if command == "/quit" or command == "/exit":
                print("👋 再见！")
                break
            
            elif command == "/help":
                print_banner()
            
            elif command == "/voices":
                voices = tts.list_voices()
                print("\n🎵 可用音色:")
                for v in voices:
                    gender = "女" if v["gender"] == "female" else "男"
                    print(f"  • {v['name']} ({v['label']}) - {gender}声 - {v['description']}")
                print()
            
            elif command == "/voice":
                if arg:
                    voice = arg
                    clone_mode = False
                    print(f"✅ 音色已切换为：{voice}")
                else:
                    print(f"💡 当前音色：{voice}")
                    print("   使用 /voice <音色名> 切换")
            
            elif command == "/clone":
                if arg:
                    if os.path.exists(arg):
                        reference_audio = arg
                        clone_mode = True
                        print(f"✅ 已启用声音克隆模式，参考音频：{arg}")
                    else:
                        print(f"❌ 文件不存在：{arg}")
                else:
                    clone_mode = not clone_mode
                    mode_str = "启用" if clone_mode else "禁用"
                    print(f"✅ 已{mode_str}声音克隆模式")
                    if clone_mode and reference_audio:
                        print(f"   参考音频：{reference_audio}")
            
            elif command == "/speed":
                if arg:
                    try:
                        speed = float(arg)
                        speed = max(0.5, min(2.0, speed))
                        print(f"✅ 语速已设置为：{speed}x")
                    except ValueError:
                        print("❌ 无效的语速值，请输入 0.5-2.0 之间的数字")
                else:
                    print(f"💡 当前语速：{speed}x")
            
            elif command == "/pitch":
                if arg:
                    try:
                        pitch = float(arg)
                        pitch = max(0.5, min(2.0, pitch))
                        print(f"✅ 音调已设置为：{pitch}x")
                    except ValueError:
                        print("❌ 无效的音调值，请输入 0.5-2.0 之间的数字")
                else:
                    print(f"💡 当前音调：{pitch}x")
            
            elif command == "/volume":
                if arg:
                    try:
                        volume = float(arg)
                        volume = max(0.1, min(1.0, volume))
                        print(f"✅ 音量已设置为：{volume*100:.0f}%")
                    except ValueError:
                        print("❌ 无效的音量值，请输入 0.1-1.0 之间的数字")
                else:
                    print(f"💡 当前音量：{volume*100:.0f}%")
            
            elif command == "/settings":
                print_settings(voice, speed, pitch, volume, clone_mode, reference_audio)
            
            else:
                print(f"❌ 未知命令：{command}")
                print("   输入 /help 查看帮助")
        
        else:
            # 合成语音
            counter += 1
            output_path = f"outputs/interactive_{counter:03d}.wav"
            
            try:
                print(f"⏳ 正在合成...")
                
                if clone_mode and reference_audio:
                    output_path = tts.synthesize_with_clone(
                        text=user_input,
                        reference_audio=reference_audio,
                        output_path=output_path,
                        speed=speed,
                        pitch=pitch,
                        volume=volume
                    )
                else:
                    output_path = tts.synthesize(
                        text=user_input,
                        voice=voice,
                        output_path=output_path,
                        speed=speed,
                        pitch=pitch,
                        volume=volume
                    )
                
                print(f"✅ 合成完成！")
                print(f"   输出文件：{output_path}")
                
            except Exception as e:
                print(f"❌ 合成失败：{e}")


if __name__ == "__main__":
    main()
