/**
 * 打字机文本组件
 */

import {useCurrentFrame, useVideoConfig} from 'remotion';

interface TypewriterTextProps {
	text: string;
	speed?: number; // 每秒显示的字符数
	from?: number;
	style?: React.CSSProperties;
	className?: string;
}

export const TypewriterText: React.FC<TypewriterTextProps> = ({
	text,
	speed = 5,
	from = 0,
	style,
}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const charactersToShow = Math.floor(((frame - from) / fps) * speed);

	if (charactersToShow <= 0) return null;

	const displayText = text.slice(0, charactersToShow);

	return (
		<span style={style}>
			{displayText}
			{charactersToShow < text.length && (
				<span
					style={{
						animation: 'blink 1s infinite',
						marginLeft: 2,
					}}
				>
					|
				</span>
			)}
		</span>
	);
};
