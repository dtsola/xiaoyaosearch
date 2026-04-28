/**
 * 场景3：v2.0.0 UI 视觉系统全面升级 + 页面展示
 * 时长：80秒 (2400帧)
 * 重点场景，展示所有升级后的页面
 */

import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {useFadeIn} from '../components/animations';
import {COLORS, FONTS, UI_PAGES} from '../types/video';

// UI页面展示卡片组件
const UIPageCard: React.FC<{
	page: typeof UI_PAGES[number];
	index: number;
}> = ({page, index}) => {
	const frame = useCurrentFrame();
	const progressInPage = frame % 300;

	// 截图显示动画（前30帧）
	const imageOpacity = progressInPage < 30 ? progressInPage / 30 : 1;
	const imageScale = progressInPage < 30 ? 0.95 + (progressInPage / 30) * 0.05 : 1;

	// 页面名称动画（0-20帧）
	const nameOpacity = progressInPage >= 0 && progressInPage < 20 ? progressInPage / 20 : 1;
	const nameTransform = progressInPage >= 0 && progressInPage < 20
		? `translateY(20px)`
		: 'translateY(0)';

	// 描述动画（10-30帧）
	const descOpacity = progressInPage >= 10 && progressInPage < 30
		? (progressInPage - 10) / 20
		: progressInPage >= 30 ? 1 : 0;
	const descTransform = progressInPage >= 10 && progressInPage < 30
		? `translateY(20px)`
		: 'translateY(0)';

	// 设计亮点动画（60+帧）
	const highlightsOpacity = progressInPage >= 60 ? 1 : 0;
	const highlightsTransform = progressInPage >= 60 && progressInPage < 80
		? `translateY(10px)`
		: 'translateY(0)';

	return (
		<>
			{/* 左侧：页面截图 */}
			<div
				style={{
					position: 'absolute',
					top: 200,
					left: 80,
					right: 480,
					bottom: 100,
					display: 'flex',
					alignItems: 'center',
					justifyContent: 'center',
				}}
			>
				<div
					style={{
						position: 'relative',
						transform: `scale(${imageScale})`,
						opacity: imageOpacity,
					}}
				>
					<Img
						src={staticFile(`images/${page.image}`)}
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
					position: 'absolute',
					top: 200,
					right: 80,
					width: 380,
				}}
			>
				{/* 页面名称 */}
				<div
					style={{
						fontSize: FONTS.heading,
						fontWeight: 700,
						color: COLORS.brandBlue,
						marginBottom: 16,
						opacity: nameOpacity,
						transform: nameTransform,
					}}
				>
					{page.name}
				</div>

				{/* 功能描述 */}
				<div
					style={{
						fontSize: FONTS.body,
						color: COLORS.textSecondary,
						lineHeight: 1.6,
						marginBottom: 32,
						opacity: descOpacity,
						transform: descTransform,
					}}
				>
					{page.desc}
				</div>

				{/* 设计亮点 */}
				<div
					style={{
						padding: 24,
						background: COLORS.bgSecondary,
						borderRadius: 8,
						border: `1px solid ${COLORS.borderStandard}`,
						opacity: highlightsOpacity,
						transform: highlightsTransform,
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
			</div>
		</>
	);
};

// 缩略图组件
const ThumbnailCard: React.FC<{
	page: typeof UI_PAGES[number];
	index: number;
}> = ({page, index}) => {
	const frame = useCurrentFrame();
	const startFrame = 60 + index * 15;
	const opacity = frame >= startFrame && frame < startFrame + 20
		? (frame - startFrame) / 20
		: frame >= startFrame + 20 ? 1 : 0;

	return (
		<div
			style={{
				opacity,
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
	);
};

// 总结部分组件
const SummarySection: React.FC = () => {
	const titleOpacity = useFadeIn(0, 30).opacity;
	const gridOpacity = useFadeIn(30, 30).opacity;

	return (
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
					opacity: titleOpacity,
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
					opacity: gridOpacity,
				}}
			>
				{UI_PAGES.map((page, index) => (
					<ThumbnailCard
						key={page.name}
						page={page}
						index={index}
					/>
				))}
			</div>
		</div>
	);
};

export const Scene3UIUpgrade: React.FC = () => {
	const frame = useCurrentFrame();

	// 顶部标题动画
	const titleOpacity = useFadeIn(0, 30).opacity;

	// 判断是否是总结部分
	const isSummary = frame >= 2100;

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
					opacity: titleOpacity,
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

			{/* 页面展示部分 */}
			{!isSummary ? (
				<UIPageCard
					page={UI_PAGES[Math.floor(frame / 300)] || UI_PAGES[0]}
					index={0}
				/>
			) : (
				<SummarySection />
			)}
		</AbsoluteFill>
	);
};
