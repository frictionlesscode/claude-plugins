import React from 'react';
import {AbsoluteFill, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {brand} from './brand';
import {Background, Caption, Device, EndCard, Highlight, RemappedVideo, ScreenIn, Shot, Still, cameraAt, useIsPortrait} from './components';

// The storyboard. Frames at 30 fps; camera `at` and video keys are scene-relative.
// Shot y is the height on the 720x1600 screen to centre; the camera returns to rest by scene end.
// Zoom only where the UI is too small to read; spotlight or tilt everywhere else.
type Scene = {
	frames: number;
	screen: React.ReactNode;
	shots?: Shot[];
	// Spotlights, scene-relative; rect is x, y, w, h as fractions of the screen.
	highlights?: {from: number; to: number; rect: [number, number, number, number]}[];
	captions: {at: number; text: string}[];
};

const TOUR = 'app-tour.mp4';

export const SCENES: Scene[] = [
	{
		// Hook: the live pace screen, the thing the app exists for.
		frames: 84,
		screen: <Still src="08-active-dark.png" />,
		highlights: [{from: 30, to: 84, rect: [0.15, 0.18, 0.7, 0.38]}],
		captions: [{at: 0, text: 'Hold the pace\nthat makes *your goal.*'}],
	},
	{
		frames: 66,
		screen: <RemappedVideo src={TOUR} keys={[[0, 0.4], [66, 1.6]]} />,
		highlights: [
			{from: 8, to: 36, rect: [0.03, 0.425, 0.94, 0.145]},
			{from: 36, to: 66, rect: [0.03, 0.585, 0.94, 0.175]},
		],
		captions: [{at: 0, text: 'Set the pace.\n*Pick the pack.*'}],
	},
	{
		// Summary: the coach note animates in, hold; scroll at 2x; hold on the result.
		frames: 186,
		screen: (
			<RemappedVideo
				src={TOUR}
				keys={[[0, 4.4], [28, 5.33], [70, 5.33], [100, 8.3], [186, 8.3]]}
			/>
		),
		highlights: [{from: 30, to: 72, rect: [0.03, 0.075, 0.94, 0.095]}],
		shots: [{at: 116, zoom: 1.4, y: 0.38}],
		captions: [
			{at: 0, text: 'Every ruck gets\n*a coach note.*'},
			{at: 92, text: '*0:28 ahead.*\nGoal made.'},
		],
	},
	{
		frames: 102,
		screen: <RemappedVideo src={TOUR} keys={[[0, 12.0], [12, 12.5], [52, 16.5], [102, 16.5]]} />,
		shots: [{at: 64, zoom: 1.4, y: 0.29}],
		highlights: [{from: 66, to: 102, rect: [0.025, 0.215, 0.95, 0.15]}],
		captions: [{at: 0, text: '*9 of 9*\nrucks on pace.'}],
	},
	{
		frames: 78,
		screen: <RemappedVideo src={TOUR} keys={[[0, 19.0], [78, 22.0]]} />,
		shots: [{at: 40, zoom: 1, tilt: -14}],
		captions: [{at: 0, text: 'Earn badges\n*along the way.*'}],
	},
];

const END_FRAMES = 84;
export const TOTAL_FRAMES = SCENES.reduce((n, s) => n + s.frames, 0) + END_FRAMES;

const starts = SCENES.map((_, i) => SCENES.slice(0, i).reduce((n, s) => n + s.frames, 0));
const endStart = TOTAL_FRAMES - END_FRAMES;

export const Promo: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps, width, height} = useVideoConfig();
	const portrait = useIsPortrait();

	// Device enters on a spring and leaves before the end card.
	const enter = spring({frame, fps, config: brand.motion.spring});
	const leave = interpolate(frame, [endStart - 8, endStart + 4], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
		easing: brand.motion.camera,
	});
	// Camera: push in on the whole phone. The focus height is centred where possible,
	// but the phone never shrinks out of its slot, so it only ever overflows the canvas.
	// In portrait the captions sit above it, so it only grows downward.
	const deviceH = portrait ? 1290 : 940;
	const slotTop = portrait ? 520 : 70;
	const slotBottom = slotTop + deviceH;
	const i = Math.max(0, starts.findLastIndex((st) => st <= frame));
	const scene = SCENES[Math.min(i, SCENES.length - 1)];
	const last = scene.shots?.at(-1);
	const atRest = !last || (last.zoom === 1 && !last.tilt);
	const shots = atRest ? scene.shots ?? [] : [...scene.shots!, {at: scene.frames, zoom: 1}];
	const {zoom, y, tilt} = cameraAt(frame - starts[i], shots);
	const top = Math.min(slotTop, Math.max(portrait ? slotTop : slotBottom - deviceH * zoom, (slotTop + slotBottom) / 2 - y * deviceH * zoom));
	const deviceStyle: React.CSSProperties = {
		position: 'absolute',
		left: portrait ? '50%' : '68%',
		top,
		transformOrigin: '50% 0',
		// Enters tilted and settles flat; scene tilt adds a slow 3D drift.
		transform: `translateX(-50%) translateY(${(1 - enter) * 160 + leave * 120}px) perspective(2400px) rotateY(${(1 - enter) * -28 + tilt}deg) rotateX(${(1 - enter) * 10}deg) scale(${zoom * (1 - leave * 0.08)})`,
		opacity: Math.min(enter * 1.5, 1) * (1 - leave),
	};

	const captionBox: React.CSSProperties = portrait
		? {position: 'absolute', left: 80, right: 80, top: 130, height: 340, display: 'flex', alignItems: 'center', justifyContent: 'center'}
		: {position: 'absolute', left: 150, width: width * 0.4, top: 0, bottom: 0, display: 'flex', alignItems: 'center'};

	return (
		<AbsoluteFill>
			<Background />
			<Device height={deviceH} style={deviceStyle}>
				{SCENES.map((s, i) => (
					<Sequence key={i} from={starts[i]} durationInFrames={s.frames + brand.transition.frames}>
						<ScreenIn>
							{s.screen}
							{s.highlights?.map((h, j) => (
								<Sequence key={j} from={h.from} durationInFrames={h.to - h.from}>
									<Highlight rect={h.rect} duration={h.to - h.from} />
								</Sequence>
							))}
						</ScreenIn>
					</Sequence>
				))}
			</Device>
			{SCENES.flatMap((s, i) =>
				s.captions.map((c, j) => {
					const from = starts[i] + c.at;
					const until = j + 1 < s.captions.length ? starts[i] + s.captions[j + 1].at : starts[i] + s.frames;
					return (
						<Sequence key={`${i}-${j}`} from={from} durationInFrames={until - from}>
							<div style={captionBox}>
								<Caption text={c.text} duration={until - from} align={portrait ? 'center' : 'left'} />
							</div>
						</Sequence>
					);
				}),
			)}
			<Sequence from={endStart + 6}>
				<EndCard />
			</Sequence>
		</AbsoluteFill>
	);
};
