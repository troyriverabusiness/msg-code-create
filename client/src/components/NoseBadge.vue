<template>
	<svg :width="width || size" :height="height || size" viewBox="0 0 150 150" :preserveAspectRatio="preserve" role="img" aria-label="nose">
		<g :transform="flip ? `translate(150,0) scale(-1,1)` : null">
			<path
				:d="shapePath"
				:fill="bg"
				:stroke="stroke"
				stroke-width="3"
			/>
		</g>

		<text
			v-if="showLabel"
			x="75"
			y="30"
			text-anchor="middle"
			:font-size="labelSize"
			:fill="labelColor"
			font-weight="700"
			alignment-baseline="middle"
		>
			{{ label }}
		</text>
	</svg>
</template>

<script setup>
const props = defineProps({
	label: { type: [String, Number], default: '' },
	size: { type: [Number, String], default: 80 },
	width: { type: [Number, String], default: null },
	height: { type: [Number, String], default: null },
	preserve: { type: String, default: 'xMidYMid meet' },
	showLabel: { type: Boolean, default: true },
	bg: { type: String, default: '#ffffff' },
	stroke: { type: String, default: '#d0d0d0' },
	labelColor: { type: String, default: '#111' },
	labelSize: { type: [Number, String], default: 20 },
	flip: { type: Boolean, default: false }
})

// shallower nose curve (flacher): reduced vertical control points for a flatter appearance
// moved the left start slightly right and lowered control points to flatten the front
// added a small quadratic curve near the top-right to give a rounded corner
// shallower nose curve (flacher): reduced vertical control points for a flatter appearance
// moved the left start slightly right and lowered control points to flatten the front
// added a small quadratic curve near the top-right to give a rounded corner
// shallower nose curve (flacher): reduced vertical control points for a flatter appearance
// moved the left start slightly right and lowered control points to flatten the front
// added a small quadratic curve near the top-right to give a rounded corner
// shallower nose curve (flacher): reduced vertical control points for a flatter appearance
// moved the left start slightly right and lowered control points to flatten the front
// added a small quadratic curve near the top-right to give a rounded corner
const shapePath = 'M18 110 C30 92 68 60 118 45 L132 45 Q140 45 140 53 L140 140 L18 140 Z'
</script>

<style scoped>
svg { display: block; width: 100%; height: 100%; }
</style>

