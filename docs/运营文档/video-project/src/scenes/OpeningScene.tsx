/**
 * 场景1：开场标题
 * 时长：10秒 (300帧)
 */

import {AbsoluteFill, Img, staticFile} from 'remotion';
import {useScaleIn, useFadeIn} from '../components/animations';
import {TypewriterText} from '../components/TypewriterText';
import {COLORS, FONTS} from '../types/video';

export const OpeningScene: React.FC = () => {
	const {transform: logoTransform} = useScaleIn(0, 60);
	const {opacity: subtitleOpacity} = useFadeIn(60, 30);

	return (
		<AbsoluteFill
			style={{
				background: `linear-gradient(135deg, ${COLORS.bgGradientStart} 0%, ${COLORS.bgGradientEnd} 100%)`,
				justifyContent: 'center',
				alignItems: 'center',
			}}
		>
			{/* Logo */}
			<div
				style={{
					marginBottom: 40,
					transform: logoTransform,
				}}
			>
				<Img
					src={staticFile('images/logo_256x256.png')}
					style={{
						width: 200,
						height: 200,
						objectFit: 'contain',
					}}
				/>
			</div>

			{/* 标题 */}
			<h1
				style={{
					fontSize: FONTS.title * 1.5,
					fontWeight: 'bold',
					margin: 0,
					marginBottom: 20,
					color: COLORS.textPrimary,
					textAlign: 'center',
				}}
			>
				<TypewriterText text="小遥搜索 XiaoyaoSearch" speed={8} from={30} />
			</h1>

			{/* 副标题 */}
			<div
				style={{
					fontSize: FONTS.subtitle,
					color: COLORS.textSecondary,
					opacity: subtitleOpacity,
					textAlign: 'center',
					marginBottom: 16,
				}}
			>
				本地AI搜索，今天正式开源！
			</div>

			{/* GitHub 地址 */}
			<div
				style={{
					fontSize: FONTS.body,
					color: COLORS.primary,
					fontWeight: 500,
					opacity: subtitleOpacity,
					textAlign: 'center',
				}}
			>
				https://github.com/dtsola/xiaoyaosearch
			</div>
		</AbsoluteFill>
	);
};
