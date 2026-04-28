"""
小遥搜索 v2.0.0 视频配音生成脚本
使用 Edge TTS 批量生成配音
"""

import asyncio
import edge_tts
import os
import sys

# 设置 Windows 控制台输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配音文本配置
VOICEOVER_TEXTS = {
    'scene1': '''本地 AI 搜索，隐私完全由你掌控！
100% AI 辅助开发的开源项目。
v2.0.0 正式发布，UI 全面升级。''',

    'scene2': '''从 v1.0.0 到 v2.0.0，
小遥搜索经历了 10 个版本的迭代。
从国际化、插件化架构，到云端大模型、MCP服务器，
再到 Agent Skills、云端嵌入模型，
以及飞书钉钉数据源、术语库系统。
每一次迭代，都在让小遥搜索变得更强大。''',

    # 场景3的开场和子步骤配音
    'scene3': '''v2.0.0 正式发布！这是小遥搜索历史上最大规模的 UI 视觉升级。
采用 Notion 温暖明亮设计风格。''',

    'scene3-1': '''搜索首页 - 居中布局，多模态指示器清晰展示。''',

    'scene3-2': '''文本搜索 - 实时结果展示，匹配度高亮。''',

    'scene3-3': '''语音搜索 - 30秒内语音录制，自动转文字。''',

    'scene3-4': '''图片搜索 - 上传图片即可搜索，AI理解图像。''',

    'scene3-5': '''索引管理 - 实时状态监控，一键重建索引。''',

    'scene3-6': '''设置页面 - AI模型配置，数据源管理。''',

    'scene3-7': '''术语库管理 - 多术语库集合，同义词扩展。''',

    'scene3-8': '''每一处细节都经过精心打磨。''',

    'scene4': '''语音文本图片搜索、本地隐私保护。
对开发者：100% AI 辅助开发，源码开源。''',

    'scene5': '''立即使用，本地AI搜索让知识管理更高效。
完整学习Vibe Coding实践，欢迎加入小遥社区！
Made with ❤️ by dtsola。''',
}

# 语音配置
VOICE_OPTIONS = {
    'female': 'zh-CN-XiaoxiaoNeural',  # 晓晓 - 女声
    'male': 'zh-CN-YunyangNeural',     # 云扬 - 男声
}

OUTPUT_DIR = '../public/audio'


async def generate_voiceover(scene: str, text: str, voice: str = 'female'):
    """
    生成单个场景的配音

    Args:
        scene: 场景名称
        text: 配音文本
        voice: 语音类型 ('female' 或 'male')
    """
    voice_id = VOICE_OPTIONS.get(voice, VOICE_OPTIONS['female'])
    output_file = os.path.join(OUTPUT_DIR, f'{scene}.mp3')

    print(f'正在生成 {scene}.mp3...')

    communicate = edge_tts.Communicate(text, voice_id)

    await communicate.save(output_file)

    print(f'✓ {scene}.mp3 生成成功！')


async def generate_all_voiceovers(voice: str = 'female'):
    """
    批量生成所有场景的配音

    Args:
        voice: 语音类型 ('female' 或 'male')
    """
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f'开始生成配音，使用语音: {voice}')
    print('=' * 50)

    # 依次生成每个场景的配音
    for scene, text in VOICEOVER_TEXTS.items():
        await generate_voiceover(scene, text, voice)

    print('=' * 50)
    print(f'✓ 所有配音生成完成！文件保存在: {OUTPUT_DIR}')


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='生成视频配音')
    parser.add_argument(
        '--voice',
        choices=['female', 'male'],
        default='female',
        help='选择语音类型 (默认: female - 晓晓)',
    )

    args = parser.parse_args()

    await generate_all_voiceovers(args.voice)


if __name__ == '__main__':
    asyncio.run(main())
