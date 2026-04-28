/**
 * 场景3：v2.0.0 UI 视觉系统全面升级 + 页面展示
 * 时长：约46秒 (1369帧)
 * 与配音子步骤同步
 */

import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {useFadeIn} from '../components/animations';
import {COLORS, FONTS, UI_PAGES} from '../types/video';

// UI页面展示卡片组件
const UIPageCard: React.FC<{
	page: typeof UI_PAGES[number];
	showHighlights: boolean;
}> = ({page, showHighlights}) => {
	const frame = useCurrentFrame();
	const progressInPage = frame % 150; // 假设每个页面最多150帧

	// 截图显示动画（前30帧）
	const imageOpacity = progressInPage < 30 ? progressInPage / 30 : 1;
	const imageScale = progressInPage < 30 ? 0.95 + (progressInPage / 30) * 0.05 : 1;

	// 页面名称动画
	const nameOpacity = progressInPage < 20 ? progressInPage / 20 : 1;

	// 描述动画
	const descOpacity = progressInPage >= 10 && progressInPage < 30
		? (progressInPage - 10) / 20
		: progressInPage >= 30 ? 1 : 0;

	// 设计亮点动画
	const highlightsOpacity = showHighlights && progressInPage >= 60 ? 1 : 0;

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
					}}
				>
					{page.desc}
				</div>

				{/* 设计亮点 */}
				{showHighlights && (
					<div
						style={{
							padding: 24,
							background: COLORS.bgSecondary,
							borderRadius: 8,
							border: `1px solid ${COLORS.borderStandard}`,
							opacity: highlightsOpacity,
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
		</>
	);
};

// 开场部分组件
const IntroSection: React.FC = () => {
	const {opacity} = useFadeIn(30, 30);
	return (
		<div
			style={{
				position: 'absolute',
				top: 200,
				left: 80,
				right: 80,
				bottom: 100,
				display: 'flex',
				justifyContent: 'center',
				alignItems: 'center',
				opacity,
			}}
		>
			<div
				style={{
					fontSize: FONTS.title,
					fontWeight: 700,
					color: COLORS.textPrimary,
					textAlign: 'center',
				}}
			>
				v2.0.0 正式发布！这是小遥搜索历史上最大规模的 UI 视觉升级。采用 Notion 温暖明亮设计风格。
			</div>
		</div>
	);
};

// 缩略图卡片组件
const ThumbnailCard: React.FC<{
	page: typeof UI_PAGES[number];
	index: number;
}> = ({page, index}) => {
	const frame = useCurrentFrame();
	// 每个缩略图依次淡入，间隔5帧
	const startFrame = frame >= 1274 ? (frame - 1274) : 0;
	const fadeInStart = 30 + index * 5;
	const opacity = startFrame < fadeInStart
		? 0
		: startFrame >= fadeInStart && startFrame < fadeInStart + 20
			? (startFrame - fadeInStart) / 20
			: 0.8;

	return (
		<div
			key={page.name}
			style={{
				textAlign: 'center',
			}}
		>
			<Img
				src={staticFile(`images/${page.image}`)}
				style={{
					width: '100%',
					borderRadius: 8,
					border: `1px solid ${COLORS.borderStandard}`,
					opacity,
				}}
			/>
			<div
				style={{
					fontSize: FONTS.caption,
					color: COLORS.textSecondary,
					marginTop: 8,
					opacity,
				}}
			>
				{page.name}
			</div>
		</div>
	);
};

// 结尾部分组件
const OutroSection: React.FC = () => {
	const {opacity: titleOpacity} = useFadeIn(0, 30);
	const {opacity: gridOpacity} = useFadeIn(30, 30);

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
				opacity: titleOpacity,
			}}
		>
			<div
				style={{
					fontSize: FONTS.title,
					fontWeight: 700,
					color: COLORS.textPrimary,
					textAlign: 'center',
					marginBottom: 32,
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
				{UI_PAGES.map((page, idx) => (
					<ThumbnailCard key={page.name} page={page} index={idx} />
				))}
			</div>
		</div>
	);
};

export const Scene3UIUpgrade: React.FC = () => {
	const frame = useCurrentFrame();

	// 根据配音时长划分时间段
	// 开场: 0-325帧
	// 搜索首页: 325-474帧 (149帧)
	// 文本搜索: 474-601帧 (127帧)
	// 语音搜索: 601-736帧 (135帧)
	// 图片搜索: 736-882帧 (146帧)
	// 索引管理: 882-1016帧 (134帧)
	// 设置页面: 1016-1146帧 (130帧)
	// 术语库管理: 1146-1274帧 (128帧)
	// 结尾: 1274-1369帧 (95帧)

	const currentPageIndex = Math.min(
		Math.floor((frame - 325) / 149),
		UI_PAGES.length - 1
	);

	const isIntro = frame < 325;
	const isOutro = frame >= 1274;
	const showHighlights = frame < 882; // 前4个页面显示设计亮点

	// 所有hooks必须在组件顶部调用
	const {opacity: headerOpacity} = useFadeIn(0, 30);

	// 计算各部分应该显示的状态
	const showIntro = isIntro;
	const showPageDisplay = !isIntro && !isOutro;
	const showOutro = isOutro;

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
					opacity: headerOpacity,
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

			{/* 开场部分 */}
			{showIntro && <IntroSection />}

			{/* 页面展示部分 */}
			{showPageDisplay && (
				<UIPageCard
					page={UI_PAGES[currentPageIndex]}
					showHighlights={showHighlights}
				/>
			)}

			{/* 结尾部分 */}
			{showOutro && <OutroSection />}
		</AbsoluteFill>
	);
};
