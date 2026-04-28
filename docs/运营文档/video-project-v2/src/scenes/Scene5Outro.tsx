/**
 * 场景5：双重CTA结尾
 * 时长：12秒 (360帧)
 * 同时向用户和开发者发出行动号召
 */

import {AbsoluteFill, Img, staticFile} from 'remotion';
import {useFadeIn, useBounceIn, useScaleIn} from '../components/animations';
import {COLORS, FONTS} from '../types/video';

export const Scene5Outro: React.FC = () => {
	// 用户CTA动画
	const {opacity: userOpacity} = useFadeIn(0, 30);
	const {transform: userTransform} = useBounceIn(30);

	// 开发者CTA动画
	const {opacity: devOpacity} = useFadeIn(60, 30);
	const {transform: devTransform} = useBounceIn(90);

	// 二维码区域动画
	const {opacity: qrOpacity} = useFadeIn(180, 30);

	// 结尾信息动画
	const {opacity: outroOpacity} = useFadeIn(270, 30);
	const {transform: outroTransform} = useScaleIn(270, 30);

	return (
		<AbsoluteFill
			style={{
				background: `linear-gradient(135deg, #e8f4fc 0%, #d0e8f7 40%, #b8ddf3 100%)`,
				justifyContent: 'center',
				alignItems: 'center',
				padding: 80,
			}}
		>
			{/* 用户CTA */}
			<div
				style={{
					position: 'absolute',
					top: 150,
					opacity: userOpacity,
					transform: userTransform,
				}}
			>
				<div
					style={{
						display: 'inline-block',
						padding: '20px 40px',
						background: COLORS.bgSecondary,
						borderRadius: 12,
						border: `2px solid ${COLORS.borderStandard}`,
					}}
				>
					<div
						style={{
							fontSize: FONTS.heading,
							fontWeight: 700,
							color: COLORS.textPrimary,
							marginBottom: 8,
						}}
					>
						立即使用
					</div>
					<div
						style={{
							fontSize: FONTS.body,
							color: COLORS.textSecondary,
						}}
					>
						本地 AI 搜索让知识管理更高效
					</div>
				</div>
			</div>

			{/* 开发者CTA - GitHub主按钮 */}
			<div
				style={{
					position: 'absolute',
					top: 350,
					opacity: devOpacity,
					transform: devTransform,
				}}
			>
				<div
					style={{
						display: 'inline-block',
						padding: '24px 48px',
						background: COLORS.brandBlue,
						borderRadius: 12,
						boxShadow: '0 8px 32px rgba(0,117,222,0.3)',
					}}
				>
					<div
						style={{
							fontSize: FONTS.heading,
							color: '#ffffff',
							fontWeight: 700,
							marginBottom: 8,
						}}
					>
						github.com/dtsola/xiaoyaosearch
					</div>
					<div
						style={{
							fontSize: FONTS.body,
							color: 'rgba(255,255,255,0.9)',
						}}
					>
						100% AI 辅助开发 · 完整源码文档开源
					</div>
				</div>
			</div>

			{/* 二维码区域 */}
			<div
				style={{
					position: 'absolute',
					top: 550,
					display: 'flex',
					gap: 60,
					opacity: qrOpacity,
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
							width: 280,
							height: 280,
							objectFit: 'contain',
							borderRadius: 12,
							border: `2px solid ${COLORS.brandBlue}`,
							marginBottom: 12,
							boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
						}}
					/>
					<div
						style={{
							fontSize: FONTS.body,
							color: COLORS.textSecondary,
							fontWeight: 600,
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
							width: 280,
							height: 280,
							objectFit: 'contain',
							borderRadius: 12,
							border: `2px solid ${COLORS.brandBlue}`,
							marginBottom: 12,
							boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
						}}
					/>
					<div
						style={{
							fontSize: FONTS.body,
							color: COLORS.textSecondary,
							fontWeight: 600,
						}}
					>
						用户交流群
					</div>
				</div>
			</div>

			{/* 社区邀请 */}
			<div
				style={{
					position: 'absolute',
					bottom: 100,
					left: 0,
					right: 0,
					opacity: qrOpacity,
					textAlign: 'center',
				}}
			>
				<div
					style={{
						fontSize: FONTS.body,
						color: COLORS.textPrimary,
						fontWeight: 600,
					}}
				>
					欢迎加入小遥社区
				</div>
			</div>

			{/* 结尾信息 */}
			<div
				style={{
					position: 'absolute',
					bottom: 40,
					left: 0,
					right: 0,
					opacity: outroOpacity,
					transform: outroTransform,
					textAlign: 'center',
				}}
			>
				<div
					style={{
						fontSize: FONTS.caption,
						color: COLORS.textTertiary,
					}}
				>
					Made with ❤️ by dtsola · 小遥搜索 v2.0.0
				</div>
			</div>
		</AbsoluteFill>
	);
};
