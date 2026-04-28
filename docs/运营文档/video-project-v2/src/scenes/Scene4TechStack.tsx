/**
 * 场景4：技术架构回顾
 * 时长：8秒 (240帧)
 * 双重受众：工具用户 + 开发者
 */

import {AbsoluteFill, Img, staticFile} from 'remotion';
import {useFadeIn, useSlideIn} from '../components/animations';
import {COLORS, FONTS, TECH_STACK} from '../types/video';

export const Scene4TechStack: React.FC = () => {
	// 整体标题动画
	const {opacity: titleOpacity} = useFadeIn(0, 30);

	// 对用户部分动画（前4秒）
	const {opacity: userLabelOpacity} = useFadeIn(30, 20);
	const {transform: userTransform, opacity: userContentOpacity} = useSlideIn('left', 50, 30);
	const {opacity: userContentFade} = useFadeIn(50, 30);

	// 对开发者部分动画（后4秒）
	const {opacity: devLabelOpacity} = useFadeIn(120, 20);
	const {transform: devTransform, opacity: devContentOpacity} = useSlideIn('right', 140, 30);
	const {opacity: devContentFade} = useFadeIn(140, 30);

	return (
		<AbsoluteFill
			style={{
				background: COLORS.bgPrimary,
				padding: 80,
			}}
		>
			{/* 顶部标题 */}
			<div
				style={{
					position: 'absolute',
					top: 60,
					left: 80,
					right: 80,
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
					技术架构
				</h2>
			</div>

			{/* 左侧：对用户部分 */}
			<div
				style={{
					position: 'absolute',
					top: 180,
					left: 80,
					width: 500,
				}}
			>
				{/* 用户标签 */}
				<div
					style={{
						fontSize: FONTS.caption,
						color: COLORS.textTertiary,
						marginBottom: 16,
						textTransform: 'uppercase',
						letterSpacing: '0.05em',
						opacity: userLabelOpacity,
					}}
				>
					对用户
				</div>

				{/* 技术栈列表 */}
				<div
					style={{
						padding: 32,
						background: COLORS.bgSecondary,
						borderRadius: 12,
						border: `1px solid ${COLORS.borderStandard}`,
						transform: userTransform,
						opacity: userContentFade,
					}}
				>
					<div
						style={{
							fontSize: FONTS.heading,
							fontWeight: 700,
							color: COLORS.brandBlue,
							marginBottom: 24,
						}}
					>
						核心能力
					</div>
					<div
						style={{
							fontSize: FONTS.body,
							color: COLORS.textPrimary,
							lineHeight: 2,
						}}
					>
						<div style={{marginBottom: 16}}>
							✓ 语音、文本、图片三种搜索方式
						</div>
						<div style={{marginBottom: 16}}>
							✓ 本地运行，数据完全隐私保护
						</div>
						<div style={{marginBottom: 16}}>
							✓ 支持文档、音视频深度检索
						</div>
						<div style={{marginBottom: 16}}>
							✓ 语雀、飞书、钉钉知识库集成
						</div>
						<div>
							✓ 本地+云端AI模型灵活切换
						</div>
					</div>
				</div>
			</div>

			{/* 中间：系统架构图 */}
			<div
				style={{
					position: 'absolute',
					top: 180,
					left: 620,
					right: 620,
					bottom: 100,
					opacity: titleOpacity,
				}}
			>
				<div
					style={{
						fontSize: FONTS.caption,
						color: COLORS.textTertiary,
						marginBottom: 16,
						textAlign: 'center',
						textTransform: 'uppercase',
						letterSpacing: '0.05em',
					}}
				>
					系统架构
				</div>
				<Img
					src={staticFile('images/系统架构.png')}
					style={{
						width: '100%',
						height: '100%',
						objectFit: 'contain',
						borderRadius: 12,
						border: `1px solid ${COLORS.borderStandard}`,
						boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
					}}
				/>
			</div>

			{/* 右侧：对开发者部分 */}
			<div
				style={{
					position: 'absolute',
					top: 180,
					right: 80,
					width: 500,
				}}
			>
				{/* 开发者标签 */}
				<div
					style={{
						fontSize: FONTS.caption,
						color: COLORS.textTertiary,
						marginBottom: 16,
						textTransform: 'uppercase',
						letterSpacing: '0.05em',
						opacity: devLabelOpacity,
					}}
				>
					对开发者
				</div>

				{/* 开发者信息卡片 */}
				<div
					style={{
						padding: 32,
						background: COLORS.bgSecondary,
						borderRadius: 12,
						border: `1px solid ${COLORS.borderStandard}`,
						transform: devTransform,
						opacity: devContentFade,
					}}
				>
					<div
						style={{
							fontSize: FONTS.heading,
							fontWeight: 700,
							color: COLORS.brandBlue,
							marginBottom: 20,
						}}
					>
						100% AI 辅助开发
					</div>

					<div
						style={{
							fontSize: FONTS.body,
							color: COLORS.textSecondary,
							lineHeight: 1.8,
							marginBottom: 16,
						}}
					>
						完整的 Vibe Coding 实践案例
					</div>

					<div
						style={{
							fontSize: FONTS.body,
							color: COLORS.textSecondary,
							lineHeight: 1.8,
							marginBottom: 24,
						}}
					>
						所有源码、文档全部开源！
					</div>

					<div
						style={{
							padding: '16px 20px',
							background: COLORS.brandBlue,
							borderRadius: 8,
							textAlign: 'center',
						}}
					>
						<div
							style={{
								fontSize: FONTS.caption,
								color: '#ffffff',
								fontWeight: 600,
								lineHeight: 1.4,
							}}
						>
							github.com/dtsola/xiaoyaosearch
						</div>
					</div>
				</div>
			</div>
		</AbsoluteFill>
	);
};
