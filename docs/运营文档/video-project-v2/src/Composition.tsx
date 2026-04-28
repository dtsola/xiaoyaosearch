/**
 * 小遥搜索 v2.0.0 版本宣传片主组合
 * 总时长：2分30秒 (4500帧 @ 30fps)
 *
 * 场景分配：
 * - 场景1：开场引入 (0:00-0:15) = 15秒 = 450帧
 * - 场景2：版本演进回顾 (0:15-0:50) = 35秒 = 1050帧
 * - 场景3：UI 升级展示 (0:50-2:10) = 80秒 = 2400帧
 * - 场景4：技术架构回顾 (2:10-2:18) = 8秒 = 240帧
 * - 场景5：结尾 (2:18-2:30) = 12秒 = 360帧
 */

import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {AbsoluteFill} from 'remotion';
import {Scene1Opening} from './scenes/Scene1Opening';
import {Scene2VersionHistory} from './scenes/Scene2VersionHistory';
import {Scene3UIUpgrade} from './scenes/Scene3UIUpgrade';
import {Scene4TechStack} from './scenes/Scene4TechStack';
import {Scene5Outro} from './scenes/Scene5Outro';
import {VIDEO_CONFIG} from './types/video';

export const ProductPromoV2: React.FC = () => {
	return (
		<AbsoluteFill>
			{/* 视频场景序列 */}
			<TransitionSeries>
				{/* 场景1：开场引入 (450帧) */}
				<TransitionSeries.Sequence durationInFrames={450}>
					<Scene1Opening />
				</TransitionSeries.Sequence>

				{/* 转场 */}
				<TransitionSeries.Transition
					presentation={fade()}
					timing={linearTiming({durationInFrames: 15})}
				/>

				{/* 场景2：版本演进回顾 (1050帧) */}
				<TransitionSeries.Sequence durationInFrames={1050}>
					<Scene2VersionHistory />
				</TransitionSeries.Sequence>

				{/* 转场 */}
				<TransitionSeries.Transition
					presentation={fade()}
					timing={linearTiming({durationInFrames: 15})}
				/>

				{/* 场景3：UI 升级展示 (2400帧) - 重点场景 */}
				<TransitionSeries.Sequence durationInFrames={2400}>
					<Scene3UIUpgrade />
				</TransitionSeries.Sequence>

				{/* 转场 */}
				<TransitionSeries.Transition
					presentation={fade()}
					timing={linearTiming({durationInFrames: 15})}
				/>

				{/* 场景4：技术架构回顾 (240帧) */}
				<TransitionSeries.Sequence durationInFrames={240}>
					<Scene4TechStack />
				</TransitionSeries.Sequence>

				{/* 转场 */}
				<TransitionSeries.Transition
					presentation={fade()}
					timing={linearTiming({durationInFrames: 15})}
				/>

				{/* 场景5：结尾 (360帧) */}
				<TransitionSeries.Sequence durationInFrames={360}>
					<Scene5Outro />
				</TransitionSeries.Sequence>
			</TransitionSeries>
		</AbsoluteFill>
	);
};

// 导出视频配置
export const config = VIDEO_CONFIG;
