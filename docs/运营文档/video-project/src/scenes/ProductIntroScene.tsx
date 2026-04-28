/**
 * 场景3：产品介绍
 * 时长：20秒 (600帧)
 */

import {AbsoluteFill} from 'remotion';
import {useFadeIn, useSlideIn} from '../components/animations';
import {COLORS, FONTS} from '../types/video';

interface Feature {
	icon: string;
	title: string;
	items: string[];
	position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
}

const features: Feature[] = [
	{
		icon: '🎤',
		title: '多模态输入',
		position: 'top-left',
		items: ['语音搜索：30秒内语音自动转文字', '文本搜索：AI理解语义', '图片搜索：AI理解图像内容'],
	},
	{
		icon: '🔍',
		title: '深度检索',
		position: 'top-right',
		items: ['文档：TXT/MD/Word/Excel/PPT/PDF', '音视频：MP4/AVI/MP3/WAV'],
	},
	{
		icon: '🧠',
		title: 'AI技术',
		position: 'bottom-left',
		items: ['BGE-M3 文本嵌入', 'FasterWhisper 语音识别', 'CN-CLIP 图像理解', 'Ollama 本地大模型'],
	},
	{
		icon: '🔒',
		title: '隐私安全',
		position: 'bottom-right',
		items: ['完全本地运行', '数据不上传云端', '自主可控'],
	},
];

export const ProductIntroScene: React.FC = () => {
	const {opacity: titleOpacity} = useFadeIn(0, 30);

	const {transform: topLeftTransform} = useSlideIn('left', 30, 25);
	const {opacity: topLeftOpacity} = useFadeIn(30, 25);

	const {transform: topRightTransform} = useSlideIn('right', 30, 25);
	const {opacity: topRightOpacity} = useFadeIn(30, 25);

	const {transform: bottomLeftTransform} = useSlideIn('left', 180, 25);
	const {opacity: bottomLeftOpacity} = useFadeIn(180, 25);

	const {transform: bottomRightTransform} = useSlideIn('right', 180, 25);
	const {opacity: bottomRightOpacity} = useFadeIn(180, 25);

	const getCardStyle = (position: Feature['position']) => {
		switch (position) {
			case 'top-left':
				return {
					transform: topLeftTransform,
					opacity: topLeftOpacity,
				};
			case 'top-right':
				return {
					transform: topRightTransform,
					opacity: topRightOpacity,
				};
			case 'bottom-left':
				return {
					transform: bottomLeftTransform,
					opacity: bottomLeftOpacity,
				};
			case 'bottom-right':
				return {
					transform: bottomRightTransform,
					opacity: bottomRightOpacity,
				};
		}
	};

	const renderFeatureCard = (feature: Feature) => {
		const style = getCardStyle(feature.position);

		return (
			<div
				key={feature.title}
				style={{
					background: 'white',
					borderRadius: 12,
					padding: 24,
					boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
					width: 480,
					height: 280,
					display: 'flex',
					flexDirection: 'column',
					...style,
				}}
			>
				<div style={{display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16}}>
					<span style={{fontSize: 40}}>{feature.icon}</span>
					<h3
						style={{
							fontSize: FONTS.subtitle,
							fontWeight: 'bold',
							margin: 0,
							color: COLORS.textPrimary,
						}}
					>
						{feature.title}
					</h3>
				</div>
				<ul
					style={{
						margin: 0,
						paddingLeft: 20,
						color: COLORS.textSecondary,
						fontSize: FONTS.body,
						flex: 1,
					}}
				>
					{feature.items.map((item, index) => (
						<li key={index} style={{marginBottom: 6}}>
							{item}
						</li>
					))}
				</ul>
			</div>
		);
	};

	return (
		<AbsoluteFill
			style={{
				background: `linear-gradient(135deg, ${COLORS.bgGradientStart} 0%, ${COLORS.bgGradientEnd} 100%)`,
				justifyContent: 'center',
				alignItems: 'center',
			}}
		>
			<div style={{width: '100%', padding: 60}}>
				{/* 标题 */}
				<h1
					style={{
						fontSize: FONTS.title * 1.2,
						fontWeight: 'bold',
						textAlign: 'center',
						margin: 0,
						marginBottom: 60,
						opacity: titleOpacity,
						color: COLORS.textPrimary,
					}}
				>
					小遥搜索是什么？
				</h1>

				{/* 特性卡片网格 */}
				<div
					style={{
						display: 'grid',
						gridTemplateColumns: '1fr 1fr',
						gridTemplateRows: '1fr 1fr',
						gap: 32,
						justifyItems: 'center',
					}}
				>
					{features.map(renderFeatureCard)}
				</div>
			</div>
		</AbsoluteFill>
	);
};
