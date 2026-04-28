/**
 * 动画工具函数
 */

import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

/**
 * 淡入动画
 */
export const useFadeIn = (delay = 0, duration = 30) => {
	const frame = useCurrentFrame();

	const opacity = interpolate(
		frame,
		[delay, delay + duration],
		[0, 1],
		{extrapolateRight: 'clamp'},
	);

	return {opacity};
};

/**
 * 缩放进入动画
 */
export const useScaleIn = (delay = 0, duration = 30) => {
	const frame = useCurrentFrame();

	const scale = interpolate(
		frame,
		[delay, delay + duration],
		[0, 1],
		{extrapolateRight: 'clamp'},
	);

	return {transform: `scale(${scale})`};
};

/**
 * 滑入动画
 */
export const useSlideIn = (
	direction: 'left' | 'right' | 'top' | 'bottom',
	delay = 0,
	duration = 30,
	distance = 100,
) => {
	const frame = useCurrentFrame();

	const getStartValue = () => {
		switch (direction) {
			case 'left':
				return [-distance, 0];
			case 'right':
				return [distance, 0];
			case 'top':
				return [0, -distance];
			case 'bottom':
				return [0, distance];
			default:
				return [-distance, 0];
		}
	};

	const [start, end] = getStartValue();
	const isHorizontal = direction === 'left' || direction === 'right';

	const value = interpolate(frame, [delay, delay + duration], [start, end], {
		extrapolateRight: 'clamp',
	});

	if (isHorizontal) {
		return {transform: `translateX(${value}px)`};
	}
	return {transform: `translateY(${value}px)`};
};

/**
 * 弹跳进入动画
 */
export const useBounceIn = (delay = 0) => {
	const frame = useCurrentFrame();

	const scale = spring({
		frame: frame - delay,
		fps: 30,
		config: {
			damping: 200,
			stiffness: 100,
		},
	});

	return {transform: `scale(${scale})`};
};

/**
 * 闪烁动画
 */
export const useBlink = (duration = 60, from = 0) => {
	const frame = useCurrentFrame();

	const opacity = interpolate(
		frame,
		[from, from + duration * 0.5, from + duration],
		[1, 0.3, 1],
		{
			extrapolateRight: 'clamp',
			extrapolateLeft: 'clamp',
		},
	);

	return {opacity};
};

/**
 * 打字机效果 - 获取当前应该显示的文本
 */
export const useTypewriterValue = (
	text: string,
	speed: number, // 每秒显示的字符数
	from = 0,
) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const charactersToShow = Math.floor(((frame - from) / fps) * speed);

	if (charactersToShow <= 0) return '';
	if (charactersToShow >= text.length) return text;

	return text.slice(0, charactersToShow);
};

/**
 * 手指点头动画 - 上下移动并缩放
 */
export const usePointingAnimation = (delay = 0, duration = 60) => {
	const frame = useCurrentFrame();

	// 使用正弦波创建上下循环移动
	const progress = ((frame - delay) % duration) / duration;
	const translateY = Math.sin(progress * Math.PI * 2) * 10;

	// 缩放效果配合移动
	const scale = 1 + Math.sin(progress * Math.PI * 2) * 0.1;

	return {
		transform: `translateY(${translateY}px) scale(${scale})`,
	};
};
