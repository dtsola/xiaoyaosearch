/**
 * 产品宣传视频主组合
 * 总时长：约89秒 (2673帧 @ 30fps)
 * 根据实际配音时长计算
 */

import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {AbsoluteFill, Sequence} from 'remotion';
import {OpeningScene} from '../scenes/OpeningScene';
import {PainPointsScene} from '../scenes/PainPointsScene';
import {ProductIntroScene} from '../scenes/ProductIntroScene';
import {DemoScene} from '../scenes/DemoScene';
import {TechScene} from '../scenes/TechScene';
import {CTAScene} from '../scenes/CTAScene';
import {Audio} from '@remotion/media';
import {staticFile} from 'remotion';

// 实际配音时长（基于音频文件）
// scene1: 11.66s ≈ 350帧
// scene2: 12.86s ≈ 386帧
// scene3: 19.87s ≈ 596帧
// scene4-1: 7.82s ≈ 235帧
// scene4-2: 5.47s ≈ 164帧
// scene4-3: 4.73s ≈ 142帧
// scene4-4: 6.17s ≈ 185帧
// scene5: 9.79s ≈ 294帧
// scene6: 10.25s ≈ 308帧

export const ProductPromoVideo: React.FC = () => {
	return (
		<AbsoluteFill>
			{/* 配音音轨 - 按实际配音时长依次播放 */}
			{/* 场景1配音 (0-350帧) - 11.66秒 */}
			<Sequence durationInFrames={350} layout="none">
				<Audio src={staticFile('audio/scene1.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景2配音 (350-736帧) - 12.86秒 */}
			<Sequence from={350} durationInFrames={386} layout="none">
				<Audio src={staticFile('audio/scene2.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景3配音 (736-1332帧) - 19.87秒 */}
			<Sequence from={736} durationInFrames={596} layout="none">
				<Audio src={staticFile('audio/scene3.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景4配音：4个子步骤 */}
			{/* 场景4-1配音 (1332-1567帧) - 搜索主界面 */}
			<Sequence from={1332} durationInFrames={235} layout="none">
				<Audio src={staticFile('audio/scene4-1.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景4-2配音 (1567-1731帧) - 文本搜索 */}
			<Sequence from={1567} durationInFrames={164} layout="none">
				<Audio src={staticFile('audio/scene4-2.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景4-3配音 (1731-1873帧) - 语音搜索 */}
			<Sequence from={1731} durationInFrames={142} layout="none">
				<Audio src={staticFile('audio/scene4-3.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景4-4配音 (1873-2058帧) - 图片搜索 */}
			<Sequence from={1873} durationInFrames={185} layout="none">
				<Audio src={staticFile('audio/scene4-4.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景5配音 (2058-2352帧) - 9.79秒 */}
			<Sequence from={2058} durationInFrames={294} layout="none">
				<Audio src={staticFile('audio/scene5.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景6配音 (2352-2660帧) - 10.25秒 */}
			<Sequence from={2352} durationInFrames={308} layout="none">
				<Audio src={staticFile('audio/scene6.mp3')} volume={1.0} />
			</Sequence>

			{/* 视频场景序列 */}
			<TransitionSeries>
				{/* 场景1：开场标题 (300帧) */}
				<TransitionSeries.Sequence durationInFrames={300}>
					<OpeningScene />
				</TransitionSeries.Sequence>

				{/* 转场 */}
				<TransitionSeries.Transition
					presentation={fade()}
					timing={linearTiming({durationInFrames: 15})}
				/>

				{/* 场景2：痛点引入 (450帧) */}
				<TransitionSeries.Sequence durationInFrames={450}>
					<PainPointsScene />
				</TransitionSeries.Sequence>

				{/* 转场 */}
				<TransitionSeries.Transition
					presentation={fade()}
					timing={linearTiming({durationInFrames: 15})}
				/>

				{/* 场景3：产品介绍 (600帧) */}
				<TransitionSeries.Sequence durationInFrames={600}>
					<ProductIntroScene />
				</TransitionSeries.Sequence>

				{/* 转场 */}
				<TransitionSeries.Transition
					presentation={fade()}
					timing={linearTiming({durationInFrames: 15})}
				/>

				{/* 场景4：功能演示 (750帧) */}
				<TransitionSeries.Sequence durationInFrames={750}>
					<DemoScene />
				</TransitionSeries.Sequence>

				{/* 转场 */}
				<TransitionSeries.Transition
					presentation={fade()}
					timing={linearTiming({durationInFrames: 15})}
				/>

				{/* 场景5：技术亮点 (300帧) */}
				<TransitionSeries.Sequence durationInFrames={300}>
					<TechScene />
				</TransitionSeries.Sequence>

				{/* 转场 */}
				<TransitionSeries.Transition
					presentation={fade()}
					timing={linearTiming({durationInFrames: 15})}
				/>

				{/* 场景6：行动号召 (390帧) - 增加3秒 */}
				<TransitionSeries.Sequence durationInFrames={390}>
					<CTAScene />
				</TransitionSeries.Sequence>
			</TransitionSeries>
		</AbsoluteFill>
	);
};
