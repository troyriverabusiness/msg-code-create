<template>

</template>

<script setup>
import ice1 from '@/assets/ice1.png'
import ice2 from '@/assets/ice2.png'
import regio1 from '@/assets/regio1.png'
import regio2 from '@/assets/regio2.png'

const props = defineProps({
	'direction': {
	type: String,
}
,'label': {
	type: String,
	default: ''
}})

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

