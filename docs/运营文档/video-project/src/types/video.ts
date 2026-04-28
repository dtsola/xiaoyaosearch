/**
 * 视频类型定义
 */

export interface VideoProps {
	// 视频通用属性
	title?: string;
	subtitle?: string;
}

export interface CardProps {
	title: string;
	icon?: string;
	children?: React.ReactNode;
}

export interface FeatureCardProps {
	icon: string;
	title: string;
	items: string[];
}

export interface TechStackProps {
	title: string;
	stacks: string[];
}

export interface GitHubButtonProps {
	icon: string;
	text: string;
}

// 视频配置常量
export const VIDEO_CONFIG = {
	fps: 30,
	width: 1920,
	height: 1080,
} as const;

// 颜色配置
export const COLORS = {
	primary: '#1890ff',
	secondary: '#52c41a',
	accent: '#722ed1',
	textPrimary: '#000000d9',
	textSecondary: '#00000073',
	bgGradientStart: '#f0f5ff',
	bgGradientEnd: '#e6f7ff',
} as const;

// 字体配置
export const FONTS = {
	title: 48,
	subtitle: 32,
	body: 24,
	code: 18,
} as const;
