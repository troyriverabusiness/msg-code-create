<template>
    <v-row class="ma-1">
    <v-expansion-panels>
  <v-expansion-panel
    v-for="item in items"
    :key="item.name"
    :title="item.name"
    text="Lorem ipsum dolor sit amet consectetur adipisicing elit. Commodi, ratione debitis quis est labore voluptatibus! Eaque cupiditate minima"
  ><v-expension-panel-text>
    <div class="train-sequence">
    <div v-for="coach in coaches" :key="coach.number" class="coach">
      <div class="coach-number">{{ coach.number }}</div>
      <img :src="iconFor(coach.type)" />
      <div class="details">
        <span v-if="coach.isQuiet">🔇 Ruhe</span>
        <span v-if="coach.isFamily">👨‍👩‍👧 Familie</span>
        <span v-if="coach.isBarrierefrei">♿ Rollstuhl</span>
        <span v-if="coach.hasBikes">🚲 Fahrrad</span>
      </div>
      <progress :value="coach.load" max="100"></progress>
    </div>
  </div>
  </v-expension-panel-text>
  </v-expansion-panel>
</v-expansion-panels>
</v-row>
</template>

<script setup>
import { ref } from 'vue';
    const items = ref([{name : 'Test'}, {name : 'Test2'}]);
</script>