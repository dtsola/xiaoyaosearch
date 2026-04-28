/**
 * 动画卡片组件
 */

import {useFadeIn} from './animations';

interface AnimatedCardProps {
	title: string;
	icon?: string;
	children?: React.ReactNode;
	delay?: number;
	duration?: number;
	style?: React.CSSProperties;
}

export const AnimatedCard: React.FC<AnimatedCardProps> = ({
	title,
	icon,
	children,
	delay = 0,
	duration = 30,
	style,
}) => {
	const {opacity} = useFadeIn(delay, duration);

	return (
		<div
			style={{
				background: 'white',
				borderRadius: 12,
				padding: 24,
				boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
				opacity,
				...style,
			}}
		>
			{icon && (
				<div style={{fontSize: 48, marginBottom: 16}}>{icon}</div>
			)}
			<h2
				style={{
					fontSize: 32,
					fontWeight: 'bold',
					margin: 0,
					marginBottom: 16,
					color: '#000000d9',
				}}
			>
				{title}
			</h2>
			{children}
		</div>
	);
};
