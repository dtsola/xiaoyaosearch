/**
 * 小遥搜索 v2.0.0 版本宣传片主组合
 * 总时长：约104秒 (3120帧 @ 30fps)
 * 所有场景时长与配音时长一致
 */

import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {AbsoluteFill, Sequence, Audio, staticFile} from 'remotion';
import {Scene1Opening} from './scenes/Scene1Opening';
import {Scene2VersionHistory} from './scenes/Scene2VersionHistory';
import {Scene3UIUpgrade} from './scenes/Scene3UIUpgrade';
import {Scene4TechStack} from './scenes/Scene4TechStack';
import {Scene5Outro} from './scenes/Scene5Outro';
import {VIDEO_CONFIG} from './types/video';

// 实际配音时长（基于音频文件）
// scene1: 12.00s = 360 frames
// scene2: 24.17s = 725 frames
// scene3: 10.85s = 325 frames (开场)
// scene3-1: 4.99s = 149 frames
// scene3-2: 4.25s = 127 frames
// scene3-3: 4.51s = 135 frames
// scene3-4: 4.90s = 146 frames
// scene3-5: 4.49s = 134 frames
// scene3-6: 4.34s = 130 frames
// scene3-7: 4.30s = 128 frames
// scene3-8: 3.17s = 95 frames
// scene4: 8.88s = 266 frames
// scene5: 11.69s = 350 frames

export const ProductPromoV2: React.FC = () => {
	return (
		<AbsoluteFill>
			{/* 配音音轨 - 按实际配音时长依次播放 */}
			{/* 场景1配音 (0-360帧) - 12.00秒 */}
			<Sequence durationInFrames={360} layout="none">
				<Audio src={staticFile('audio/scene1.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景2配音 (360-1085帧) - 24.17秒 */}
			<Sequence from={360} durationInFrames={725} layout="none">
				<Audio src={staticFile('audio/scene2.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景3配音：开场 + 8个子步骤 */}
			{/* 场景3开场 (1085-1410帧) - 10.85秒 */}
			<Sequence from={1085} durationInFrames={325} layout="none">
				<Audio src={staticFile('audio/scene3.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景3-1配音 (1410-1559帧) - 搜索首页 */}
			<Sequence from={1410} durationInFrames={149} layout="none">
				<Audio src={staticFile('audio/scene3-1.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景3-2配音 (1559-1686帧) - 文本搜索 */}
			<Sequence from={1559} durationInFrames={127} layout="none">
				<Audio src={staticFile('audio/scene3-2.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景3-3配音 (1686-1821帧) - 语音搜索 */}
			<Sequence from={1686} durationInFrames={135} layout="none">
				<Audio src={staticFile('audio/scene3-3.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景3-4配音 (1821-1967帧) - 图片搜索 */}
			<Sequence from={1821} durationInFrames={146} layout="none">
				<Audio src={staticFile('audio/scene3-4.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景3-5配音 (1967-2101帧) - 索引管理 */}
			<Sequence from={1967} durationInFrames={134} layout="none">
				<Audio src={staticFile('audio/scene3-5.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景3-6配音 (2101-2231帧) - 设置页面 */}
			<Sequence from={2101} durationInFrames={130} layout="none">
				<Audio src={staticFile('audio/scene3-6.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景3-7配音 (2231-2359帧) - 术语库管理 */}
			<Sequence from={2231} durationInFrames={128} layout="none">
				<Audio src={staticFile('audio/scene3-7.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景3-8配音 (2359-2454帧) - 场景3结尾 */}
			<Sequence from={2359} durationInFrames={95} layout="none">
				<Audio src={staticFile('audio/scene3-8.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景4配音 (2454-2720帧) - 8.88秒 */}
			<Sequence from={2454} durationInFrames={266} layout="none">
				<Audio src={staticFile('audio/scene4.mp3')} volume={1.0} />
			</Sequence>

			{/* 场景5配音 (2720-3070帧) - 11.69秒 */}
			<Sequence from={2720} durationInFrames={350} layout="none">
				<Audio src={staticFile('audio/scene5.mp3')} volume={1.0} />
			</Sequence>

			{/* 视频场景序列 */}
			<TransitionSeries>
				{/* 场景1：开场引入 (360帧) - 与配音时长一致 */}
				<TransitionSeries.Sequence durationInFrames={360}>
					<Scene1Opening />
				</TransitionSeries.Sequence>

				{/* 转场 */}
				<TransitionSeries.Transition
					presentation={fade()}
					timing={linearTiming({durationInFrames: 15})}
				/>

				{/* 场景2：版本演进回顾 (725帧) - 与配音时长一致 */}
				<TransitionSeries.Sequence durationInFrames={725}>
					<Scene2VersionHistory />
				</TransitionSeries.Sequence>

				{/* 转场 */}
				<TransitionSeries.Transition
					presentation={fade()}
					timing={linearTiming({durationInFrames: 15})}
				/>

				{/* 场景3：UI 升级展示 (1369帧) - 与配音时长一致 */}
				<TransitionSeries.Sequence durationInFrames={1369}>
					<Scene3UIUpgrade />
				</TransitionSeries.Sequence>

				{/* 转场 */}
				<TransitionSeries.Transition
					presentation={fade()}
					timing={linearTiming({durationInFrames: 15})}
				/>

				{/* 场景4：技术架构回顾 (266帧) - 与配音时长一致 */}
				<TransitionSeries.Sequence durationInFrames={266}>
					<Scene4TechStack />
				</TransitionSeries.Sequence>

				{/* 转场 */}
				<TransitionSeries.Transition
					presentation={fade()}
					timing={linearTiming({durationInFrames: 15})}
				/>

				{/* 场景5：结尾 (350帧) - 与配音时长一致 */}
				<TransitionSeries.Sequence durationInFrames={350}>
					<Scene5Outro />
				</TransitionSeries.Sequence>
			</TransitionSeries>
		</AbsoluteFill>
	);
};

// 导出视频配置
export const config = VIDEO_CONFIG;
