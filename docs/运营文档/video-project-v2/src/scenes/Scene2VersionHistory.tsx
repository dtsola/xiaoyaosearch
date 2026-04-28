/**
 * 场景2：版本演进回顾
 * 时长：35秒 (1050帧)
 * 展示 v1.1.0 到 v1.9.0 共9个版本
 */

import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {useFadeIn} from '../components/animations';
import {COLORS, FONTS, VERSION_HISTORY} from '../types/video';

// 版本卡片组件
const VersionCard: React.FC<{
	version: typeof VERSION_HISTORY[number];
	index: number;
}> = ({version, index}) => {
	const frame = useCurrentFrame();
	const startFrame = 150 + index * 90;

	// 计算动画状态
	const opacity = frame < startFrame
		? 0
		: frame < startFrame + 30
			? (frame - startFrame) / 30
			: 1;

	const translateY = frame < startFrame
		? -50
		: frame < startFrame + 30
			? -50 + ((frame - startFrame) / 30) * 50
			: 0;

	return (
		<div
			style={{
				padding: 32,
				background: COLORS.bgSecondary,
				borderRadius: 12,
				border: `1px solid ${COLORS.borderStandard}`,
				opacity,
				transform: `translateY(${translateY}px)`,
			}}
		>
			{/* 版本号 */}
			<div
				style={{
					fontSize: FONTS.heading,
					fontWeight: 700,
					color: COLORS.brandBlue,
					marginBottom: 12,
				}}
			>
				{version.version}
			</div>

			{/* 发布日期 */}
			<div
				style={{
					fontSize: FONTS.caption,
					color: COLORS.textTertiary,
					marginBottom: 16,
				}}
			>
				{version.date}
			</div>

			{/* 功能特性 */}
			<div
				style={{
					fontSize: FONTS.body,
					color: COLORS.textSecondary,
					lineHeight: 1.5,
				}}
			>
				{version.feature}
			</div>
		</div>
	);
};

export const Scene2VersionHistory: React.FC = () => {
	const frame = useCurrentFrame();

	// 开场过渡（5秒 = 150帧）
	const {opacity: titleOpacity} = useFadeIn(0, 30);
	const {opacity: subtitleOpacity} = useFadeIn(30, 30);

	// 底部总结的动画
	const summaryOpacity = frame >= 900
		? (frame >= 900 && frame < 930
			? (frame - 900) / 30
			: 1)
		: 0;

	return (
		<AbsoluteFill
			style={{
				background: COLORS.bgPrimary,
				justifyContent: 'center',
				alignItems: 'center',
				padding: 80,
			}}
		>
			{/* 标题 */}
			<div
				style={{
					position: 'absolute',
					top: 100,
					left: 80,
					opacity: titleOpacity,
				}}
			>
				<h2
					style={{
						fontSize: FONTS.title,
						fontWeight: 700,
						margin: 0,
						color: COLORS.textPrimary,
						letterSpacing: '-0.02em',
					}}
				>
					从 v1.0.0 到 v2.0.0
				</h2>
			</div>

			{/* 副标题 */}
			<div
				style={{
					position: 'absolute',
					top: 180,
					left: 80,
					opacity: subtitleOpacity,
				}}
			>
				<div
					style={{
						fontSize: FONTS.body,
						color: COLORS.textSecondary,
					}}
				>
					小遥搜索经历了 10 个版本的迭代
				</div>
			</div>

			{/* 版本卡片网格 */}
			<div
				style={{
					display: 'grid',
					gridTemplateColumns: 'repeat(3, 1fr)',
					gap: 32,
					width: '100%',
					maxWidth: 1600,
					marginTop: 120,
				}}
			>
				{VERSION_HISTORY.map((version, index) => (
					<VersionCard
						key={version.version}
						version={version}
						index={index}
					/>
				))}
			</div>

			{/* 底部总结 */}
			<div
				style={{
					position: 'absolute',
					bottom: 100,
					opacity: summaryOpacity,
				}}
			>
				<div
					style={{
						fontSize: FONTS.subtitle,
						fontWeight: 600,
						color: COLORS.textPrimary,
						textAlign: 'center',
					}}
				>
					每一次迭代，都在让小遥搜索变得更强大
				</div>
			</div>
		</AbsoluteFill>
	);
};
