import React from 'react';
import {Composition} from 'remotion';
import {Promo, TOTAL_FRAMES} from './Promo';

// Same storyboard, two layouts: the components reframe themselves by aspect ratio.
export const Root: React.FC = () => (
	<>
		<Composition id="Landscape" component={Promo} durationInFrames={TOTAL_FRAMES} fps={30} width={1920} height={1080} />
		<Composition id="Portrait" component={Promo} durationInFrames={TOTAL_FRAMES} fps={30} width={1080} height={1920} />
	</>
);
