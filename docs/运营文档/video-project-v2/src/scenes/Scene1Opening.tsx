/**
 * 场景1：开场引入
 * 时长：15秒 (450帧)
 * 前3秒抓住用户注意力
 */

import {AbsoluteFill, Img, staticFile} from 'remotion';
import {useFadeIn, useScaleIn, useTypewriterValue} from '../components/animations';
import {COLORS, FONTS} from '../types/video';

export const Scene1Opening: React.FC = () => {
	const {transform: imageTransform} = useScaleIn(0, 90, 0.9);
	const {opacity: taglineOpacity} = useFadeIn(120, 30);
	const {opacity: versionOpacity} = useFadeIn(390, 30);

	// 主标题打字机效果（前3秒）
	const mainTitle = useTypewriterValue('本地 AI 搜索', 8, 0);
	const subTitle = useTypewriterValue('隐私完全由你掌控！', 10, 30);
	const developerTagline = useTypewriterValue('100% AI 辅助开发的开源项目！', 12, 60);

	return (
		<AbsoluteFill
			style={{
				background: `linear-gradient(135deg, #e8f4fc 0%, #d0e8f7 40%, #b8ddf3 100%)`,
				justifyContent: 'center',
				alignItems: 'center',
			}}
		>
			{/* 产品主界面大图 */}
			<div
				style={{
					position: 'absolute',
					inset: 0,
					opacity: 0.30,
					transform: imageTransform,
				}}
			>
				<Img
					src={staticFile('images/小遥搜索.png')}
					style={{
						width: '100%',
						height: '100%',
						objectFit: 'cover',
					}}
				/>
			</div>

			{/* 内容容器 */}
			<div
				style={{
					position: 'relative',
					zIndex: 1,
					textAlign: 'center',
				}}
			>
				{/* 主标题 - 3秒内完成 */}
				<h1
					style={{
						fontSize: FONTS.title * 1.2,
						fontWeight: 700,
						margin: 0,
						marginBottom: 20,
						color: COLORS.textPrimary,
						letterSpacing: '-0.02em',
					}}
				>
					{mainTitle}
				</h1>

				{/* 副标题 - 3秒内完成 */}
				<div
					style={{
						fontSize: FONTS.subtitle,
						color: COLORS.textSecondary,
						marginBottom: 32,
						minHeight: 48,
					}}
				>
					{subTitle}
				</div>

				{/* 开发者标语 - 3-6秒 */}
				<div
					style={{
						fontSize: FONTS.body,
						color: COLORS.brandBlue,
						fontWeight: 600,
						marginBottom: 48,
						minHeight: 36,
						opacity: taglineOpacity,
					}}
				>
					{developerTagline}
				</div>

				{/* 产品介绍（6-13秒） */}
				<div
					style={{
						fontSize: FONTS.body,
						color: COLORS.textSecondary,
						lineHeight: 1.6,
						maxWidth: 900,
						opacity: taglineOpacity,
					}}
				>
					支持语音、文本、图片三种输入，深度检索本地文档、音视频内容。
				</div>

				{/* 版本发布提示（最后2秒） */}
				<div
					style={{
						marginTop: 40,
						padding: '16px 32px',
						background: COLORS.brandBlue,
						borderRadius: 8,
						opacity: versionOpacity,
					}}
				>
					<div
						style={{
							fontSize: FONTS.heading,
							color: '#ffffff',
							fontWeight: 600,
						}}
					>
						v2.0.0 正式发布，UI 全面升级！
					</div>
				</div>
			</div>
		</AbsoluteFill>
	);
};
