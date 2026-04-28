/**
 * 场景6：行动号召
 * 时长：10秒 (300帧)
 */

import {AbsoluteFill, Img, staticFile} from 'remotion';
import {useScaleIn, useBounceIn, useFadeIn, usePointingAnimation} from '../components/animations';
import {COLORS, FONTS} from '../types/video';

const githubButtons = [
	{icon: '⭐', text: 'Star 本项目', color: '#333'},
	{icon: '🍴', text: 'Fork 参与贡献', color: '#333'},
	{icon: '👀', text: 'Watch 关注更新', color: '#333'},
];

const contributeItems = [
	'插件系统开发',
	'多数据源连接器',
	'UI/UX 优化',
	'性能优化',
];

export const CTAScene: React.FC = () => {
	// 主标题缩放进入
	const {transform: titleTransform} = useScaleIn(0, 40);

	// Logo 缩放进入
	const {transform: logoTransform} = useScaleIn(0, 40);

	// GitHub 地址淡入
	const {opacity: urlOpacity} = useFadeIn(30, 30);

	// 手指指引动画
	const {transform: pointingTransform} = usePointingAnimation(60, 45);

	// GitHub 按钮依次弹入
	const {transform: btn1Transform} = useBounceIn(60);
	const {transform: btn2Transform} = useBounceIn(90);
	const {transform: btn3Transform} = useBounceIn(120);

	// 贡献者招募淡入
	const {opacity: contributeOpacity} = useFadeIn(180, 30);

	return (
		<AbsoluteFill
			style={{
				background: `linear-gradient(135deg, ${COLORS.bgGradientStart} 0%, ${COLORS.bgGradientEnd} 100%)`,
				justifyContent: 'center',
				alignItems: 'center',
			}}
		>
			<div style={{textAlign: 'center'}}>
				{/* 主标题 */}
				<h1
					style={{
						fontSize: FONTS.title * 1.5,
						fontWeight: 'bold',
						margin: 0,
						marginBottom: 20,
						transform: titleTransform,
						color: COLORS.textPrimary,
					}}
				>
					今天正式开源！
				</h1>

				{/* Logo */}
				<div
					style={{
						marginBottom: 30,
						transform: logoTransform,
						display: 'flex',
						justifyContent: 'center',
						alignItems: 'center',
					}}
				>
					<Img
						src={staticFile('images/logo_256x256.png')}
						style={{
							width: 120,
							height: 120,
							objectFit: 'contain',
						}}
					/>
				</div>

				{/* GitHub 地址 */}
				<div
					style={{
						fontSize: FONTS.subtitle,
						color: COLORS.primary,
						fontWeight: 500,
						marginBottom: 40,
						opacity: urlOpacity,
						display: 'flex',
						alignItems: 'center',
						justifyContent: 'center',
						gap: 12,
					}}
				>
					https://github.com/dtsola/xiaoyaosearch
					{/* 手指指引 */}
					<span
						style={{
							fontSize: 32,
							transform: pointingTransform,
						}}
					>
						👆
					</span>
				</div>

				{/* GitHub 按钮组 */}
				<div
					style={{
						display: 'flex',
						gap: 20,
						justifyContent: 'center',
						marginBottom: 50,
					}}
				>
					{githubButtons.map((btn, index) => {
						const transforms = [btn1Transform, btn2Transform, btn3Transform];
						return (
							<div
								key={btn.text}
								style={{
									background: 'white',
									borderRadius: 8,
									padding: '16px 24px',
									boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
									display: 'flex',
									alignItems: 'center',
									gap: 12,
									transform: transforms[index],
								}}
							>
								<span style={{fontSize: 32}}>{btn.icon}</span>
								<span
									style={{
										fontSize: FONTS.body,
										fontWeight: 500,
										color: btn.color,
									}}
								>
									{btn.text}
								</span>
							</div>
						);
					})}
				</div>

				{/* 贡献者招募 */}
				<div
					style={{
						background: 'white',
						borderRadius: 12,
						padding: '24px 32px',
						boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
						opacity: contributeOpacity,
						display: 'inline-block',
					}}
				>
					<h3
						style={{
							fontSize: FONTS.subtitle,
							fontWeight: 'bold',
							margin: 0,
							marginBottom: 16,
							color: COLORS.primary,
						}}
					>
						期待你的贡献
					</h3>
					<div
						style={{
							display: 'flex',
							gap: 16,
							fontSize: FONTS.body,
							color: COLORS.textSecondary,
						}}
					>
						{contributeItems.map((item, index) => (
							<span key={index}>
								{index > 0 && <span style={{margin: '0 8px'}}>•</span>}
								{item}
							</span>
						))}
					</div>
				</div>
			</div>
		</AbsoluteFill>
	);
};
