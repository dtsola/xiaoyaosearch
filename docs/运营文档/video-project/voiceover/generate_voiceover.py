"""
小遥搜索视频配音生成脚本
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
	'scene1': '''我做了一个本地AI搜索工具，今天正式开源了！
支持语音、文本、图片多模态输入，100% AI辅助编程实现。''',

	'scene2': '''文件太多找不到？搜索只能匹配文件名？
隐私数据要上传云端？AI工具配置太复杂？
小遥搜索，一次解决所有痛点！''',

	'scene3': '''小遥搜索支持语音、文本、图片多模态输入。
深度检索TXT、Word、PDF等文档，还有音视频内容。
集成BGE-M3、FasterWhisper等AI模型。
完全本地运行，数据不上传云端，安全可控。''',

	# 场景4的子步骤配音
	'scene4-1': '''来看实际操作。这是搜索主界面，支持语音、文本、图片三种搜索方式。''',
	'scene4-2': '''文本搜索：输入关键词，AI理解语义，精准匹配。''',
	'scene4-3': '''语音搜索：点击录音，语音自动转文字搜索。''',
	'scene4-4': '''图片搜索：上传图片，AI分析图像内容，找到相关文件。''',

	'scene5': '''前端Electron加Vue3，后端Python FastAPI。
最重要的是，这个项目100%通过Vibe Coding实现！''',

	'scene6': '''今天正式开源！欢迎Star、Fork、关注更新。
插件开发、数据源连接、UI优化，期待你的贡献！''',
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
