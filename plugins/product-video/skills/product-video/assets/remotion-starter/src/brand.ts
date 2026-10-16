import {loadFont} from '@remotion/fonts';
import {Easing, staticFile} from 'remotion';

// Everything a future RuckPace video should reuse. Colours come from the app's
// theme (ui/theme/Color.kt); the font is the app's own Manrope.
export const brand = {
	name: 'RuckPace',
	tagline: 'A pace coach for rucking.',
	colors: {
		bgTop: '#0C1A12',
		bgBottom: '#173524',
		glow: '#4A9460', // LightPrimary
		accent: '#7FBF92', // DarkPrimary
		ink: '#F2F3F2', // DarkInkColor
		muted: '#9AA0A2', // DarkMutedColor
		bezel: '#0A0C0D',
	},
	font: {
		family: 'Manrope',
		files: {500: 'fonts/manrope_medium.ttf', 600: 'fonts/manrope_semibold.ttf', 700: 'fonts/manrope_bold.ttf'},
	},
	device: {
		screenAspect: 720 / 1600, // the source recordings
		bezel: 14,
		radius: 58,
		shadow: '0 50px 140px rgba(0,0,0,0.55), 0 0 0 1.5px rgba(255,255,255,0.09)',
	},
	caption: {
		size: {landscape: 86, portrait: 78},
		weight: 700,
		lineHeight: 1.08,
		letterSpacing: '-0.02em',
		staggerFrames: 3, // between words
		rise: 34, // px each word travels in
		outFrames: 8,
	},
	transition: {frames: 9, fromScale: 1.035}, // screen-to-screen crossfade
	motion: {
		spring: {damping: 16, mass: 0.7, stiffness: 140},
		camera: Easing.bezier(0.33, 0, 0.15, 1),
		cameraFrames: 14, // ~470 ms per push
	},
} as const;

for (const [weight, file] of Object.entries(brand.font.files)) {
	loadFont({family: brand.font.family, url: staticFile(file), weight});
}
