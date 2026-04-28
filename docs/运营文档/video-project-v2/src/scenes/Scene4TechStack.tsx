/**
 * 场景4：技术架构回顾
 * 时长：8秒 (240帧)
 * 双重受众：工具用户 + 开发者
 */

import {AbsoluteFill, Img, staticFile} from 'remotion';
import {useFadeIn, useSlideIn} from '../components/animations';
import {COLORS, FONTS, TECH_STACK} from '../types/video';

export const Scene4TechStack: React.FC = () => {
	// 对用户部分（前4秒）
	const {opacity: userOpacity} = useFadeIn(0, 30);
	const {transform: userTransform} = useSlideIn('left', 30, 30);
	const {opacity: userContentOpacity} = useFadeIn(30, 30);

	// 对开发者部分（后4秒）
	const {transform: devTransform} = useSlideIn('right', 150, 30);
	const {opacity: devContentOpacity} = useFadeIn(150, 30);

	return (
		<AbsoluteFill
			style={{
				background: COLORS.bgPrimary,
				padding: 80,
			}}
		>
			{/* 系统架构图 */}
			<div
				style={{
					position: 'absolute',
					top: 80,
					right: 80,
					width: 500,
					opacity: 0.1,
				}}
			>
				<Img
					src={staticFile('images/系统架构.png')}
					style={{
						width: '100%',
						objectFit: 'contain',
					}}
				/>
			</div>

			{/* 对用户部分 */}
			<div
				style={{
					position: 'absolute',
					top: 80,
					left: 80,
					opacity: userOpacity,
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
					对用户
				</div>
				<h2
					style={{
						fontSize: FONTS.title,
						fontWeight: 700,
						margin: 0,
						color: COLORS.textPrimary,
						marginBottom: 24,
					}}
				>
					技术架构
				</h2>
			</div>

			{/* 技术栈列表 */}
			<div
				style={{
					position: 'absolute',
					top: 200,
					left: 80,
					transform: userTransform,
					opacity: userContentOpacity,
				}}
			>
				<div
					style={{
						fontSize: FONTS.body,
						color: COLORS.textPrimary,
						lineHeight: 1.8,
					}}
				>
					<div style={{marginBottom: 16}}>
						<strong style={{color: COLORS.brandBlue}}>前端：</strong>
						{TECH_STACK.frontend.join(' + ')}
					</div>
					<div style={{marginBottom: 16}}>
						<strong style={{color: COLORS.brandBlue}}>后端：</strong>
						{TECH_STACK.backend.join(' + ')}
					</div>
					<div style={{marginBottom: 16}}>
						<strong style={{color: COLORS.brandBlue}}>AI 模型：</strong>
						{TECH_STACK.ai.join(' + ')}
					</div>
					<div>
						<strong style={{color: COLORS.brandBlue}}>搜索引擎：</strong>
						{TECH_STACK.search.join(' + ')}
					</div>
				</div>
			</div>

			{/* 对开发者部分 */}
			<div
				style={{
					position: 'absolute',
					top: 200,
					right: 80,
					width: 500,
					transform: devTransform,
					opacity: devContentOpacity,
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
					对开发者
				</div>

				<div
					style={{
						padding: 32,
						background: COLORS.bgSecondary,
						borderRadius: 12,
						border: `1px solid ${COLORS.borderStandard}`,
					}}
				>
					<div
						style={{
							fontSize: FONTS.heading,
							fontWeight: 700,
							color: COLORS.brandBlue,
							marginBottom: 16,
						}}
					>
						100% AI 辅助开发
					</div>

					<div
						style={{
							fontSize: FONTS.body,
							color: COLORS.textSecondary,
							lineHeight: 1.6,
							marginBottom: 12,
						}}
					>
						完整的 Vibe Coding 实践案例
					</div>

					<div
						style={{
							fontSize: FONTS.body,
							color: COLORS.textSecondary,
							lineHeight: 1.6,
						}}
					>
						所有源码、文档全部开源！
					</div>
				</div>
			</div>
		</AbsoluteFill>
	);
};
