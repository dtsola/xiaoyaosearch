/**
 * 场景3：v2.0.0 UI 视觉系统全面升级 + 页面展示
 * 时长：80秒 (2400帧)
 * 重点场景，展示所有升级后的页面
 */

import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {useFadeIn, useScaleIn, useSlideIn} from '../components/animations';
import {COLORS, FONTS, UI_PAGES} from '../types/video';

export const Scene3UIUpgrade: React.FC = () => {
	const frame = useCurrentFrame();

	// 每个页面展示约 10 秒（300帧），前3秒介绍，后7秒展示截图
	// 页面1: 0-300帧
	// 页面2: 300-600帧
	// 页面3: 600-900帧
	// 页面4: 900-1200帧
	// 页面5: 1200-1500帧
	// 页面6: 1500-1800帧
	// 页面7: 1800-2100帧
	// 总结: 2100-2400帧

	const getCurrentPage = () => {
		const pageIndex = Math.floor(frame / 300);
		return UI_PAGES[pageIndex] || UI_PAGES[UI_PAGES.length - 1];
	};

	const progressInPage = frame % 300;
	const isSummary = frame >= 2100;

	const currentPage = getCurrentPage();

	return (
		<AbsoluteFill
			style={{
				background: COLORS.bgPrimary,
			}}
		>
			{/* 顶部标题 */}
			<div
				style={{
					position: 'absolute',
					top: 60,
					left: 80,
					right: 80,
					display: 'flex',
					justifyContent: 'space-between',
					alignItems: 'center',
				}}
			>
				<div>
					<h2
						style={{
							fontSize: FONTS.title,
							fontWeight: 700,
							margin: 0,
							color: COLORS.textPrimary,
							letterSpacing: '-0.02em',
						}}
					>
						v2.0.0 正式发布！
					</h2>
					<div
						style={{
							fontSize: FONTS.body,
							color: COLORS.textSecondary,
							marginTop: 8,
						}}
					>
						这是小遥搜索历史上最大规模的 UI 视觉升级
					</div>
				</div>

				{/* 设计风格标签 */}
				<div
					style={{
						padding: '12px 24px',
						background: COLORS.bgSecondary,
						borderRadius: 8,
						border: `1px solid ${COLORS.borderStandard}`,
					}}
				>
					<div
						style={{
							fontSize: FONTS.body,
							color: COLORS.brandBlue,
							fontWeight: 600,
						}}
					>
						Notion 温暖明亮设计风格
					</div>
				</div>
			</div>

			{/* 主内容区 */}
			{!isSummary ? (
				// 页面展示
				<div
					style={{
						position: 'absolute',
						top: 200,
						left: 80,
						right: 80,
						bottom: 100,
						display: 'flex',
						gap: 48,
					}}
				>
					{/* 左侧：页面截图 */}
					<div
						style={{
							flex: 1,
							display: 'flex',
							alignItems: 'center',
							justifyContent: 'center',
						}}
					>
						<div
							style={{
								position: 'relative',
								transform: useScaleIn(progressInPage, 30, 0.95).transform,
								opacity: useFadeIn(progressInPage, 15).opacity,
							}}
						>
							<Img
								src={staticFile(`images/${currentPage.image}`)}
								style={{
									width: '100%',
									maxWidth: 900,
									borderRadius: 12,
									boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
								}}
							/>
						</div>
					</div>

					{/* 右侧：功能说明 */}
					<div
						style={{
							width: 400,
							display: 'flex',
							flexDirection: 'column',
							justifyContent: 'center',
						}}
					>
						{/* 页面名称 */}
						<div
							style={{
								fontSize: FONTS.heading,
								fontWeight: 700,
								color: COLORS.brandBlue,
								marginBottom: 16,
								transform: useSlideIn('right', progressInPage, 20).transform,
								opacity: useFadeIn(progressInPage, 20).opacity,
							}}
						>
							{currentPage.name}
						</div>

						{/* 功能描述 */}
						<div
							style={{
								fontSize: FONTS.body,
								color: COLORS.textSecondary,
								lineHeight: 1.6,
								marginBottom: 32,
								transform: useSlideIn('right', progressInPage + 10, 20).transform,
								opacity: useFadeIn(progressInPage + 10, 20).opacity,
							}}
						>
							{currentPage.desc}
						</div>

						{/* 设计亮点 */}
						{progressInPage > 60 && (
							<div
								style={{
									padding: 24,
									background: COLORS.bgSecondary,
									borderRadius: 8,
									border: `1px solid ${COLORS.borderStandard}`,
									transform: useSlideIn('right', progressInPage + 30, 20).transform,
									opacity: useFadeIn(progressInPage + 30, 20).opacity,
								}}
							>
								<div
									style={{
										fontSize: FONTS.caption,
										color: COLORS.textTertiary,
										marginBottom: 8,
										textTransform: 'uppercase',
										letterSpacing: '0.05em',
									}}
								>
									设计亮点
								</div>
								<div
									style={{
										fontSize: FONTS.body,
										color: COLORS.textPrimary,
										fontWeight: 500,
									}}
								>
									纯白背景 + 品牌蓝色
								</div>
								<div
									style={{
										fontSize: FONTS.body,
										color: COLORS.textPrimary,
										fontWeight: 500,
									}}
								>
									多层阴影堆叠
								</div>
							</div>
						)}
					</div>
				</div>
			) : (
				// 总结
				<div
					style={{
						position: 'absolute',
						top: 200,
						left: 80,
						right: 80,
						bottom: 100,
						display: 'flex',
						flexDirection: 'column',
						justifyContent: 'center',
						alignItems: 'center',
					}}
				>
					<div
						style={{
							fontSize: FONTS.title,
							fontWeight: 700,
							color: COLORS.textPrimary,
							textAlign: 'center',
							marginBottom: 32,
							opacity: useFadeIn(0, 30).opacity,
						}}
					>
						每一处细节都经过精心打磨
					</div>

					{/* 所有页面缩略图网格 */}
					<div
						style={{
							display: 'grid',
							gridTemplateColumns: 'repeat(4, 1fr)',
							gap: 24,
							opacity: useFadeIn(30, 30).opacity,
						}}
					>
						{UI_PAGES.map((page, index) => (
							<div
								key={page.name}
								style={{
									opacity: useFadeIn(60 + index * 15, 20).opacity,
								}}
							>
								<div
									style={{
										fontSize: FONTS.caption,
										color: COLORS.textSecondary,
										marginBottom: 8,
										textAlign: 'center',
									}}
								>
									{page.name}
								</div>
								<Img
									src={staticFile(`images/${page.image}`)}
									style={{
										width: '100%',
										borderRadius: 8,
										border: `1px solid ${COLORS.borderStandard}`,
									}}
								/>
							</div>
						))}
					</div>
				</div>
			)}
		</AbsoluteFill>
	);
};
