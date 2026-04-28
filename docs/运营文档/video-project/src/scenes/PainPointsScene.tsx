/**
 * 场景2：痛点引入
 * 时长：15秒 (450帧)
 */

import {AbsoluteFill} from 'remotion';
import {useSlideIn, useScaleIn, useFadeIn} from '../components/animations';
import {COLORS, FONTS} from '../types/video';

interface PainPointCard {
	icon: string;
	text: string;
}

const painPoints: PainPointCard[] = [
	{icon: '📁', text: '文件太多找不到？'},
	{icon: '🔍', text: '搜索只能匹配文件名？'},
	{icon: '🔒', text: '隐私数据要上传云端？'},
	{icon: '🤖', text: 'AI工具配置太复杂？'},
];

export const PainPointsScene: React.FC = () => {
	const {transform: card1Transform} = useSlideIn('right', 0, 20);
	const {opacity: card1Opacity} = useFadeIn(0, 20);
	const {transform: card2Transform} = useSlideIn('right', 90, 20);
	const {opacity: card2Opacity} = useFadeIn(90, 20);
	const {transform: card3Transform} = useSlideIn('right', 180, 20);
	const {opacity: card3Opacity} = useFadeIn(180, 20);
	const {transform: card4Transform} = useSlideIn('right', 270, 20);
	const {opacity: card4Opacity} = useFadeIn(270, 20);

	const {transform: solutionTransform} = useScaleIn(360);
	const {opacity: solutionOpacity} = useFadeIn(360, 30);

	const renderCard = (card: PainPointCard, index: number) => {
		const transforms = [
			card1Transform,
			card2Transform,
			card3Transform,
			card4Transform,
		];
		const opacities = [
			card1Opacity,
			card2Opacity,
			card3Opacity,
			card4Opacity,
		];

		return (
			<div
				key={index}
				style={{
					background: 'white',
					borderRadius: 12,
					padding: '24px 32px',
					boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
					display: 'flex',
					alignItems: 'center',
					gap: 16,
					transform: transforms[index],
					opacity: opacities[index],
				}}
			>
				<span style={{fontSize: 48}}>{card.icon}</span>
				<span
					style={{
						fontSize: FONTS.subtitle,
						fontWeight: 500,
						color: COLORS.textPrimary,
					}}
				>
					{card.text}
				</span>
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
			<div
				style={{
					display: 'flex',
					flexDirection: 'column',
					gap: 24,
				}}
			>
				{painPoints.map((point, index) => renderCard(point, index))}

				{/* 解决方案 */}
				<div
					style={{
						background: COLORS.primary,
						borderRadius: 12,
						padding: '24px 32px',
						boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
						display: 'flex',
						alignItems: 'center',
						gap: 16,
						transform: solutionTransform,
						opacity: solutionOpacity,
					}}
				>
					<span style={{fontSize: 48}}>✨</span>
					<span
						style={{
							fontSize: FONTS.title,
							fontWeight: 'bold',
							color: 'white',
						}}
					>
						小遥搜索，一次解决所有痛点！
					</span>
				</div>
			</div>
		</AbsoluteFill>
	);
};
