/**
 * 场景5：开源邀请 + 结尾
 * 时长：12秒 (360帧)
 * 双重行动号召
 */

import {AbsoluteFill, Img, staticFile} from 'remotion';
import {useFadeIn, useScaleIn, useBounceIn} from '../components/animations';
import {COLORS, FONTS} from '../types/video';

export const Scene5Outro: React.FC = () => {
	// 用户行动号召（前6秒）
	const {opacity: userOpacity} = useFadeIn(0, 30);
	const {transform: userTransform} = useBounceIn(30);

	// 开发者行动号召（6-9秒）
	const {opacity: devOpacity} = useFadeIn(180, 30);
	const {transform: devTransform} = useBounceIn(210);

	// 结尾信息（最后3秒）
	const {opacity: outroOpacity} = useFadeIn(270, 30);
	const {transform: outroTransform} = useScaleIn(270, 30);

	return (
		<AbsoluteFill
			style={{
				background: `linear-gradient(135deg, ${COLORS.gradientStart} 0%, ${COLORS.gradientEnd} 100%)`,
				justifyContent: 'center',
				alignItems: 'center',
			}}
		>
			{/* 用户行动号召 */}
			<div
				style={{
					position: 'absolute',
					top: 200,
					left: 80,
					right: 80,
					opacity: userOpacity,
					transform: userTransform,
				}}
			>
				<div
					style={{
						textAlign: 'center',
					}}
				>
					<div
						style={{
							fontSize: FONTS.caption,
							color: COLORS.textTertiary,
							marginBottom: 16,
							textTransform: 'uppercase',
							letterSpacing: '0.05em',
						}}
					>
						立即使用
					</div>
					<h2
						style={{
							fontSize: FONTS.title,
							fontWeight: 700,
							margin: 0,
							marginBottom: 24,
							color: COLORS.textPrimary,
						}}
					>
						本地 AI 搜索让知识管理更高效！
					</h2>
				</div>
			</div>

			{/* 开发者行动号召 */}
			<div
				style={{
					position: 'absolute',
					top: 380,
					left: 80,
					right: 80,
					opacity: devOpacity,
					transform: devTransform,
				}}
			>
				<div
					style={{
						textAlign: 'center',
					}}
				>
					<div
						style={{
							fontSize: FONTS.caption,
							color: COLORS.textTertiary,
							marginBottom: 16,
							textTransform: 'uppercase',
							letterSpacing: '0.05em',
						}}
					>
						开发者
					</div>
					<h2
						style={{
							fontSize: FONTS.title,
							fontWeight: 700,
							margin: 0,
							marginBottom: 24,
							color: COLORS.textPrimary,
						}}
					>
						完整学习 Vibe Coding 实践
					</h2>

					{/* GitHub 链接 */}
					<div
						style={{
							display: 'inline-block',
							padding: '16px 32px',
							background: COLORS.brandBlue,
							borderRadius: 8,
							color: '#ffffff',
							fontSize: FONTS.body,
							fontWeight: 600,
						}}
					>
						github.com/dtsola/xiaoyaosearch
					</div>
				</div>
			</div>

			{/* 二维码展示 */}
			<div
				style={{
					position: 'absolute',
					bottom: 200,
					display: 'flex',
					gap: 48,
					opacity: devOpacity,
					transform: devTransform,
				}}
			>
				<div
					style={{
						textAlign: 'center',
					}}
				>
					<Img
						src={staticFile('images/开发者交流群图.png')}
						style={{
							width: 150,
							height: 150,
							borderRadius: 12,
							border: `1px solid ${COLORS.borderStandard}`,
							marginBottom: 12,
						}}
					/>
					<div
						style={{
							fontSize: FONTS.caption,
							color: COLORS.textSecondary,
						}}
					>
						开发者交流群
					</div>
				</div>

				<div
					style={{
						textAlign: 'center',
					}}
				>
					<Img
						src={staticFile('images/用户交流群图.png')}
						style={{
							width: 150,
							height: 150,
							borderRadius: 12,
							border: `1px solid ${COLORS.borderStandard}`,
							marginBottom: 12,
						}}
					/>
					<div
						style={{
							fontSize: FONTS.caption,
							color: COLORS.textSecondary,
						}}
					>
						用户交流群
					</div>
				</div>
			</div>

			{/* 结尾信息 */}
			<div
				style={{
					position: 'absolute',
					bottom: 60,
					opacity: outroOpacity,
					transform: outroTransform,
					textAlign: 'center',
				}}
			>
				<div
					style={{
						fontSize: FONTS.body,
						color: COLORS.textSecondary,
						marginBottom: 8,
					}}
				>
					欢迎加入小遥社区，获取最新动态
				</div>
				<div
					style={{
						fontSize: FONTS.heading,
						fontWeight: 600,
						color: COLORS.textPrimary,
					}}
				>
					Made with ❤️ by dtsola
				</div>
				<div
					style={{
						fontSize: FONTS.caption,
						color: COLORS.textTertiary,
						marginTop: 8,
					}}
				>
					小遥搜索 v2.0.0 - 2026年4月24日
				</div>
			</div>
		</AbsoluteFill>
	);
};
