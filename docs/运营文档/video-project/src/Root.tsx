import './index.css';
import {Composition, Folder} from 'remotion';
import {ProductPromoVideo} from './compositions/ProductPromoVideo';

// 计算总时长（基于实际配音时长）
// scene1: 11.66s ≈ 350帧
// scene2: 12.86s ≈ 386帧
// scene3: 19.87s ≈ 596帧
// scene4-1: 7.82s ≈ 235帧
// scene4-2: 5.47s ≈ 164帧
// scene4-3: 4.73s ≈ 142帧
// scene4-4: 6.17s ≈ 185帧
// scene5: 9.79s ≈ 294帧
// scene6: 10.25s ≈ 308帧
// 总计: 2660帧 (约88.7秒)
// 场景6画面时长: 390帧 (13秒)
const TOTAL_DURATION = 350 + 386 + 596 + 235 + 164 + 142 + 185 + 294 + 308;

export const RemotionRoot: React.FC = () => {
	return (
		<>
			<Folder name="小遥搜索宣传视频">
				<Composition
					id="ProductPromo"
					component={ProductPromoVideo}
					durationInFrames={TOTAL_DURATION}
					fps={30}
					width={1920}
					height={1080}
					defaultProps={{}}
				/>
			</Folder>
		</>
	);
};
