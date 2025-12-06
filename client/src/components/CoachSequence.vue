<template>
  <v-card class="coach-sequence-card">
    <v-card-title>Coach Sequence</v-card-title>
    <v-card-text>
      <!-- Platform sectors display -->
      <div class="platform-display">
        <div class="platform-track-label">
          <span class="track-number">Gl. 14</span>
          <span class="direction-label">Abfahrtsrichtung →</span>
        </div>
        <div class="platform-sectors">
          <div class="sector" v-for="sector in ['F', 'E', 'D', 'C', 'B', 'A']" :key="sector">
            {{ sector }}
          </div>
        </div>
      </div>
      
      <div class="coaches-container">
        <!-- left nose shape -->
        <div class="loco-nose">
          <NoseBadge :label="coaches && coaches.length ? coaches[0].number : ''" :width="'100px'" :height="'100%'" :preserve="'none'" :showLabel="false" bg="#f9f9f9" stroke="rgb(217,48,40)" />
        </div>

        <div
          v-for="coach in coaches"
          :key="coach.number"
          class="coach-item"
          :class="{ 'coach-disabled': !coach.available }"
        >
          <div class="coach-header">
            <span class="coach-number">{{ coach.number }}</span>
            <span class="coach-type">{{ coach.type }}</span>
          </div>
          <div class="coach-amenities">
            <span v-if="coach.isQuiet" class="amenity-badge quiet" title="Quiet zone">🔇</span>
            <span v-if="coach.isFamily" class="amenity-badge family" title="Family zone">👨‍👩‍👧</span>
            <span v-if="coach.isBarrierefrei" class="amenity-badge accessible" title="Wheelchair accessible">♿</span>
            <span v-if="coach.hasBikes" class="amenity-badge bikes" title="Bikes allowed">🚲</span>
          </div>
          <div class="coach-load">
            <v-progress-linear :value="coach.load" height="6" rounded />
            <span class="load-text">{{ coach.load }}%</span>
          </div>
        </div>

        <!-- right nose shape -->
        <div class="loco-nose">
          <NoseBadge :label="coaches && coaches.length ? coaches[coaches.length-1].number : ''" :width="'100px'" :height="'100%'" :preserve="'none'" :showLabel="false" bg="#f9f9f9" stroke="rgb(217,48,40)" :flip="true" />
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import NoseBadge from '@/components/NoseBadge.vue'

const props = defineProps({'coaches': {
  type: Array,
  required: true,
  default: () => []
}})

</script>

<style scoped>
.coach-sequence-card {
  margin: 16px 0;
}

/* Platform sectors display */
.platform-display {
  margin-bottom: 12px;
}

.platform-track-label {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-bottom: 6px;
}

.track-number {
  background: #003366;
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-weight: 700;
  font-size: 13px;
}

.direction-label {
  font-size: 12px;
  color: #333;
  font-weight: 500;
}

.platform-sectors {
  display: flex;
  justify-content: space-between;
  background: #e8f1fa;
  border: 2px solid #003366;
  border-radius: 4px;
  padding: 4px 6px;
  gap: 1px;
}

.sector {
  background: #003366;
  color: white;
  width: 26px;
  height: 26px;
  min-width: 26px;
  max-width: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 3px;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
}

.coaches-container {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 8px 0;
  flex-wrap: nowrap;
  -webkit-overflow-scrolling: touch;
}

.coach-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border: 2px solid rgb(217, 46, 40);
  border-radius: 8px;
  background: #f9f9f9;
  min-width: 100px;
  flex-shrink: 0;
  text-align: center;
  transition: all 0.2s ease;
  cursor: pointer;
}

.coach-item:hover {
  background: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(217, 46, 40, 0.15);
}

.coach-item.coach-disabled {
  opacity: 0.5;
  border-color: #ccc;
  background: #e8e8e8;
  cursor: not-allowed;
}

.coach-header {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.coach-number {
  font-size: 18px;
  font-weight: 700;
  color: rgb(217, 46, 40);
}

.coach-type {
  font-size: 10px;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.coach-icon {
  font-size: 28px;
}

.coach-amenities {
  display: flex;
  gap: 4px;
  justify-content: center;
  flex-wrap: wrap;
  min-height: 24px;
}

.amenity-badge {
  font-size: 14px;
  cursor: help;
}

.coach-load {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.load-text {
  font-size: 11px;
  color: #666;
  font-weight: 600;
}

/* Nose shapes at both ends */
.loco-nose {
  display: flex;
  align-items: stretch;
  justify-content: center;
  flex: 0 0 100px;
  flex-shrink: 0;
  margin: 0 6px;
}
.loco-nose svg { width: 100%; height: 100%; }
</style>
