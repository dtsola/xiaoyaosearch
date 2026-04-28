/**
 * 场景2：版本演进回顾
 * 时长：35秒 (1050帧)
 * 展示 v1.1.0 到 v1.9.0 共9个版本
 */

import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {useFadeIn, useFadeSlideIn} from '../components/animations';
import {COLORS, FONTS, VERSION_HISTORY} from '../types/video';

export const Scene2VersionHistory: React.FC = () => {
	const frame = useCurrentFrame();

	// 开场过渡（5秒 = 150帧）
	const {opacity: titleOpacity} = useFadeIn(0, 30);
	const {opacity: subtitleOpacity} = useFadeIn(30, 30);

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
				{VERSION_HISTORY.map((version, index) => {
					// 每个版本从 150+90*index 帧开始出现
					const startFrame = 150 + index * 90;
					const {opacity, transform} = useFadeSlideIn('top', startFrame, 30);

					return (
						<div
							key={version.version}
							style={{
								padding: 32,
								background: COLORS.bgSecondary,
								borderRadius: 12,
								border: `1px solid ${COLORS.borderStandard}`,
								opacity,
								transform,
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
				})}
			</div>

			{/* 底部总结（最后5秒） */}
			{frame > 900 && (
				<div
					style={{
						position: 'absolute',
						bottom: 100,
						opacity: useFadeIn(900, 30).opacity,
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
			)}
		</AbsoluteFill>
	);
};
