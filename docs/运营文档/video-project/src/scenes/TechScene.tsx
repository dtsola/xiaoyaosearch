/**
 * 场景5：技术亮点
 * 时长：10秒 (300帧)
 */

import {AbsoluteFill, Img, staticFile} from 'remotion';
import {useFadeIn, useSlideIn, useBlink} from '../components/animations';
import {COLORS, FONTS} from '../types/video';

const techStacks = [
	{label: '前端', value: 'Electron + Vue 3 + TypeScript'},
	{label: '后端', value: 'Python 3.10 + FastAPI'},
	{label: 'AI引擎', value: 'BGE-M3 + FasterWhisper + CN-CLIP + Ollama'},
	{label: '搜索', value: 'Faiss + Whoosh'},
	{label: '数据库', value: 'SQLite'},
];

export const TechScene: React.FC = () => {
	const {opacity: titleOpacity} = useFadeIn(0, 20);

	// 技术栈逐行淡入
	const {opacity: stack1Opacity} = useFadeIn(20, 15);
	const {opacity: stack2Opacity} = useFadeIn(40, 15);
	const {opacity: stack3Opacity} = useFadeIn(60, 15);
	const {opacity: stack4Opacity} = useFadeIn(80, 15);
	const {opacity: stack5Opacity} = useFadeIn(100, 15);

	// Vibe Coding 标签闪烁
	const {opacity: vibeOpacity} = useBlink(90, 130);

	// 架构图滑入
	const {transform: archTransform} = useSlideIn('right', 160, 30);
	const {opacity: archOpacity} = useFadeIn(160, 30);

	const stackOpacities = [
		stack1Opacity,
		stack2Opacity,
		stack3Opacity,
		stack4Opacity,
		stack5Opacity,
	];

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
						marginBottom: 50,
						opacity: titleOpacity,
						color: COLORS.textPrimary,
					}}
				>
					技术架构
				</h1>

				<div
					style={{
						display: 'flex',
						gap: 60,
						alignItems: 'center',
						justifyContent: 'center',
					}}
				>
					{/* 技术栈列表 */}
					<div
						style={{
							background: 'white',
							borderRadius: 12,
							padding: 32,
							boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
						}}
					>
						{techStacks.map((stack, index) => (
							<div
								key={stack.label}
								style={{
									marginBottom: index < techStacks.length - 1 ? 20 : 0,
									opacity: stackOpacities[index],
								}}
							>
								<div
									style={{
										fontSize: FONTS.body,
										fontWeight: 'bold',
										color: COLORS.primary,
										marginBottom: 4,
									}}
								>
									{stack.label}
								</div>
								<div
									style={{
										fontSize: FONTS.code,
										color: COLORS.textSecondary,
										fontFamily: 'monospace',
									}}
								>
									{stack.value}
								</div>
							</div>
						))}

						{/* Vibe Coding 标签 */}
						<div
							style={{
								marginTop: 24,
								padding: '12px 20px',
								background: COLORS.accent,
								borderRadius: 8,
								textAlign: 'center',
								opacity: vibeOpacity,
							}}
						>
							<span
								style={{
									fontSize: FONTS.body,
									fontWeight: 'bold',
									color: 'white',
								}}
							>
								✨ 100% Vibe Coding 实现！
							</span>
						</div>
					</div>

					{/* 系统架构图 */}
					<div
						style={{
							background: 'white',
							borderRadius: 12,
							padding: 20,
							boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
							transform: archTransform,
							opacity: archOpacity,
						}}
					>
						<Img
							src={staticFile('images/系统架构.png')}
							style={{
								height: 400,
								width: 'auto',
								borderRadius: 8,
							}}
						/>
					</div>
				</div>
			</div>
		</AbsoluteFill>
	);
};
