import React from 'react';
import {
	AbsoluteFill,
	Freeze,
	Img,
	OffthreadVideo,
	interpolate,
	spring,
	staticFile,
	useCurrentFrame,
	useVideoConfig,
} from 'remotion';
import {brand} from './brand';

export const useIsPortrait = () => {
	const {width, height} = useVideoConfig();
	return height > width;
};

/** Dark brand gradient with a slow-drifting glow behind the device. */
export const Background: React.FC = () => {
	const frame = useCurrentFrame();
	const portrait = useIsPortrait();
	const gx = (portrait ? 50 : 66) + Math.sin(frame / 90) * 4;
	const gy = (portrait ? 62 : 50) + Math.cos(frame / 110) * 4;
	const {bgTop, bgBottom, glow} = brand.colors;
	return (
		<AbsoluteFill
			style={{
				background: `radial-gradient(circle at ${gx}% ${gy}%, ${glow}55 0%, transparent 45%), linear-gradient(160deg, ${bgTop}, ${bgBottom})`,
			}}
		/>
	);
};

/** A plain modern phone: bezel, rounded screen, deep shadow. Height drives size. */
export const Device: React.FC<{height: number; style?: React.CSSProperties; children: React.ReactNode}> = ({
	height,
	style,
	children,
}) => {
	const {bezel, radius, shadow, screenAspect} = brand.device;
	const screenH = height - bezel * 2;
	return (
		<div
			style={{
				width: screenH * screenAspect + bezel * 2,
				height,
				padding: bezel,
				borderRadius: radius,
				background: brand.colors.bezel,
				boxShadow: shadow,
				...style,
			}}
		>
			<div style={{position: 'relative', width: '100%', height: '100%', borderRadius: radius - bezel, overflow: 'hidden', background: '#FAFAF9'}}>
				{children}
			</div>
		</div>
	);
};

type Key = [frame: number, value: number];
const remap = (frame: number, keys: Key[]) =>
	interpolate(frame, keys.map((k) => k[0]), keys.map((k) => k[1]), {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

/**
 * Plays a recording on a remapped clock: keys are [outputFrame, sourceSeconds].
 * Flat segments are freeze frames, steep ones are speed ramps.
 */
export const RemappedVideo: React.FC<{src: string; keys: Key[]}> = ({src, keys}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	return (
		<Freeze frame={Math.round(remap(frame, keys) * fps)}>
			<OffthreadVideo src={staticFile(src)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
		</Freeze>
	);
};

export const Still: React.FC<{src: string}> = ({src}) => (
	<Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top'}} />
);

/** A camera move on the device. Shot = frame it arrives by, zoom, focus height (0-1 of the screen), 3D tilt in degrees. */
export type Shot = {at: number; zoom: number; y?: number; tilt?: number};

export const cameraAt = (frame: number, shots: Shot[]) => {
	const {cameraFrames, camera} = brand.motion;
	let zoom = 1;
	let y = 0.5;
	let tilt = 0;
	let prev: Shot = {at: 0, zoom: 1, y: 0.5};
	for (const shot of shots) {
		const t = interpolate(frame, [shot.at - cameraFrames, shot.at], [0, 1], {
			extrapolateLeft: 'clamp',
			extrapolateRight: 'clamp',
			easing: camera,
		});
		zoom = prev.zoom + (shot.zoom - prev.zoom) * t;
		y = (prev.y ?? 0.5) + ((shot.y ?? 0.5) - (prev.y ?? 0.5)) * t;
		tilt = (prev.tilt ?? 0) + ((shot.tilt ?? 0) - (prev.tilt ?? 0)) * t;
		if (frame < shot.at) break;
		prev = shot;
	}
	return {zoom, y, tilt};
};

/** Spotlight: dims the screen around a rect (fractions of the screen) and rings it in the accent. */
export const Highlight: React.FC<{rect: [x: number, y: number, w: number, h: number]; duration: number}> = ({
	rect: [x, y, w, h],
	duration,
}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const p = spring({frame, fps, config: brand.motion.spring});
	const out = interpolate(frame, [duration - 8, duration], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const t = Math.min(p, out);
	return (
		<div
			style={{
				position: 'absolute',
				left: `${x * 100}%`,
				top: `${y * 100}%`,
				width: `${w * 100}%`,
				height: `${h * 100}%`,
				borderRadius: 22,
				border: `4px solid ${brand.colors.glow}`,
				boxShadow: `0 0 0 9999px rgba(8, 20, 13, ${0.45 * t}), 0 0 40px ${brand.colors.accent}88`,
				opacity: t,
				transform: `scale(${1.06 - 0.06 * p})`,
			}}
		/>
	);
};

/** Crossfade-and-settle used when a new screen replaces the previous one. */
export const ScreenIn: React.FC<{children: React.ReactNode}> = ({children}) => {
	const frame = useCurrentFrame();
	const {frames, fromScale} = brand.transition;
	const t = interpolate(frame, [0, frames], [0, 1], {extrapolateRight: 'clamp', easing: brand.motion.camera});
	return <AbsoluteFill style={{opacity: t, transform: `scale(${fromScale - (fromScale - 1) * t})`}}>{children}</AbsoluteFill>;
};

/** Words rise in one by one; *asterisks* mark accent words. Fades out at the end. */
export const Caption: React.FC<{text: string; duration: number; align?: 'left' | 'center'}> = ({
	text,
	duration,
	align = 'left',
}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const portrait = useIsPortrait();
	const c = brand.caption;
	const out = interpolate(frame, [duration - c.outFrames, duration], [1, 0], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	let accent = false;
	let index = 0;
	const lines = text.split('\n').map((line) =>
		line.split(' ').map((raw) => {
			if (raw.startsWith('*')) accent = true;
			const word = {text: raw.replace(/\*/g, ''), accent, i: index++};
			if (raw.endsWith('*') || raw.endsWith('*.')) accent = false;
			return word;
		}),
	);
	return (
		<div
			style={{
				fontFamily: brand.font.family,
				fontWeight: c.weight,
				fontSize: portrait ? c.size.portrait : c.size.landscape,
				lineHeight: c.lineHeight,
				letterSpacing: c.letterSpacing,
				color: brand.colors.ink,
				textAlign: align,
				opacity: out,
				transform: `translateY(${(1 - out) * -12}px)`,
			}}
		>
			{lines.map((words, l) => (
				<div key={l}>
					{words.map((w) => {
						const p = spring({frame: frame - w.i * c.staggerFrames, fps, config: brand.motion.spring});
						return (
							<span
								key={w.i}
								style={{
									display: 'inline-block',
									marginRight: '0.24em',
									opacity: Math.min(1, p * 1.4),
									transform: `translateY(${(1 - p) * c.rise}px)`,
									color: w.accent ? brand.colors.accent : undefined,
								}}
							>
								{w.text}
							</span>
						);
					})}
				</div>
			))}
		</div>
	);
};

/** Icon, name and tagline. */
export const EndCard: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const portrait = useIsPortrait();
	const pop = spring({frame, fps, config: brand.motion.spring});
	const text = spring({frame: frame - 6, fps, config: brand.motion.spring});
	const icon = portrait ? 300 : 260;
	return (
		<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', fontFamily: brand.font.family, color: brand.colors.ink}}>
			<Img
				src={staticFile('icon.png')}
				style={{
					width: icon,
					height: icon,
					borderRadius: icon * 0.23,
					boxShadow: brand.device.shadow,
					transform: `scale(${0.6 + 0.4 * pop})`,
					opacity: pop,
				}}
			/>
			<div style={{marginTop: 56, textAlign: 'center', opacity: text, transform: `translateY(${(1 - text) * 24}px)`}}>
				<div style={{fontSize: portrait ? 104 : 96, fontWeight: 700, letterSpacing: '-0.03em'}}>{brand.name}</div>
				<div style={{fontSize: portrait ? 44 : 40, fontWeight: 500, color: brand.colors.muted, marginTop: 10}}>{brand.tagline}</div>
			</div>
		</AbsoluteFill>
	);
};
