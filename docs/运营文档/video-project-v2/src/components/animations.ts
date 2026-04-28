/**
 * v2.0 动画工具函数
 * 基于 Remotion 动画 API
 */

import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

/**
 * 淡入动画
 * @param delay 延迟帧数
 * @param duration 动画持续帧数
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
 * 淡出动画
 * @param delay 延迟帧数
 * @param duration 动画持续帧数
 */
export const useFadeOut = (delay = 0, duration = 30) => {
	const frame = useCurrentFrame();

	const opacity = interpolate(
		frame,
		[delay, delay + duration],
		[1, 0],
		{extrapolateRight: 'clamp'},
	);

	return {opacity};
};

/**
 * 缩放进入动画
 * @param delay 延迟帧数
 * @param duration 动画持续帧数
 * @param from 起始缩放值，默认 0.8
 */
export const useScaleIn = (delay = 0, duration = 30, from = 0.8) => {
	const frame = useCurrentFrame();

	const scale = interpolate(
		frame,
		[delay, delay + duration],
		[from, 1],
		{extrapolateRight: 'clamp'},
	);

	return {transform: `scale(${scale})`};
};

/**
 * 滑入动画
 * @param direction 滑入方向
 * @param delay 延迟帧数
 * @param duration 动画持续帧数
 * @param distance 滑动距离（像素）
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
 * @param delay 延迟帧数
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
 * 打字机效果 - 获取当前应该显示的文本
 * @param text 完整文本
 * @param speed 每秒显示的字符数
 * @param from 开始帧数
 */
export const useTypewriterValue = (
	text: string,
	speed: number,
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
 * 闪烁动画
 * @param duration 动画周期帧数
 * @param from 开始帧数
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
 * 脉冲动画（缩放 + 透明度）
 * @param delay 延迟帧数
 * @param duration 动画周期帧数
 */
export const usePulse = (delay = 0, duration = 60) => {
	const frame = useCurrentFrame();

	const progress = ((frame - delay) % duration) / duration;

	const scale = 1 + Math.sin(progress * Math.PI * 2) * 0.05;
	const opacity = 0.8 + Math.sin(progress * Math.PI * 2) * 0.2;

	return {
		transform: `scale(${scale})`,
		opacity,
	};
};

/**
 * 组合动画：淡入 + 滑入
 * @param direction 滑入方向
 * @param delay 延迟帧数
 * @param duration 动画持续帧数
 */
export const useFadeSlideIn = (
	direction: 'left' | 'right' | 'top' | 'bottom',
	delay = 0,
	duration = 30,
) => {
	const {opacity} = useFadeIn(delay, duration);
	const slideResult = useSlideIn(direction, delay, duration, 50);

	return {
		opacity,
		...slideResult,
	};
};
