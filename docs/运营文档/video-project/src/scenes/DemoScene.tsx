/**
 * 场景4：功能演示
 * 时长：25秒 (750帧)
 */

import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {useFadeIn, useSlideIn} from '../components/animations';
import {COLORS, FONTS} from '../types/video';

interface DemoStep {
	title: string;
	image: string;
	description: string;
	startFrame: number;
}

const demoSteps: DemoStep[] = [
	{
		title: '搜索主界面',
		image: 'images/搜索界面-主界面.png',
		description: '支持语音、文本、图片三种搜索方式',
		startFrame: 0,
	},
	{
		title: '文本搜索',
		image: 'images/搜索界面-文本搜索.png',
		description: '输入关键词，AI理解语义，精准匹配',
		startFrame: 180,
	},
	{
		title: '语音搜索',
		image: 'images/搜索界面-语音搜索.png',
		description: '点击录音，语音自动转文字搜索',
		startFrame: 360,
	},
	{
		title: '图片搜索',
		image: 'images/搜索界面-图片搜索.png',
		description: '上传图片，AI分析图像内容',
		startFrame: 540,
	},
];

export const DemoScene: React.FC = () => {
	const frame = useCurrentFrame();

	// 计算当前显示哪个演示步骤
	const getCurrentStep = () => {
		for (let i = demoSteps.length - 1; i >= 0; i--) {
			if (frame >= demoSteps[i].startFrame) {
				return demoSteps[i];
			}
		}
		return demoSteps[0];
	};

	const currentStep = getCurrentStep();
	const stepIndex = demoSteps.findIndex((s) => s.title === currentStep.title);

	// 标题淡入
	const {opacity: titleOpacity} = useFadeIn(0, 20);

	// 截图滑入动画
	const {transform: imageTransform} = useSlideIn('bottom', 0, 20);
	const {opacity: imageOpacity} = useFadeIn(0, 20);

	// 描述文字动画
	const {opacity: descOpacity} = useFadeIn(30, 20);

	return (
		<AbsoluteFill
			style={{
				background: `linear-gradient(135deg, ${COLORS.bgGradientStart} 0%, ${COLORS.bgGradientEnd} 100%)`,
			}}
		>
			<div style={{width: '100%', height: '100%', padding: 60}}>
				{/* 标题 */}
				<h1
					style={{
						fontSize: FONTS.title * 1.2,
						fontWeight: 'bold',
						textAlign: 'center',
						margin: 0,
						marginBottom: 40,
						opacity: titleOpacity,
						color: COLORS.textPrimary,
					}}
				>
					来看实际操作
				</h1>

				{/* 主内容区 */}
				<div
					style={{
						display: 'flex',
						flexDirection: 'column',
						alignItems: 'center',
						gap: 32,
					}}
				>
					{/* 步骤指示器 */}
					<div
						style={{
							display: 'flex',
							gap: 16,
						}}
					>
						{demoSteps.map((step, index) => (
							<div
								key={step.title}
								style={{
									width: 12,
									height: 12,
									borderRadius: '50%',
									background: index === stepIndex ? COLORS.primary : '#ccc',
								}}
							/>
						))}
					</div>

					{/* 当前步骤标题 */}
					<h2
						style={{
							fontSize: FONTS.title,
							fontWeight: 'bold',
							margin: 0,
							color: COLORS.primary,
						}}
					>
						{currentStep.title}
					</h2>

					{/* 界面截图 */}
					<div
						style={{
							background: 'white',
							borderRadius: 12,
							padding: 20,
							boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
							transform: imageTransform,
							opacity: imageOpacity,
						}}
					>
						<Img
							src={staticFile(currentStep.image)}
							style={{
								height: 500,
								width: 'auto',
								borderRadius: 8,
							}}
						/>
					</div>

					{/* 描述文字 */}
					<p
						style={{
							fontSize: FONTS.body,
							color: COLORS.textSecondary,
							textAlign: 'center',
							margin: 0,
							opacity: descOpacity,
							maxWidth: 800,
						}}
					>
						{currentStep.description}
					</p>
				</div>
			</div>
		</AbsoluteFill>
	);
};
