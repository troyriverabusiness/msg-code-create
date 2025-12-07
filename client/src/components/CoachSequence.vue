<template>
  <div>
    <v-card class="coach-sequence-card">
      <v-card-title>Wagenreihung</v-card-title>
      <v-card-text>
      <div class="platform-display">
        <div class="platform-track-label">
          <span class="track-number">Gl. 14</span>
          <span class="direction-label">Fahrtrichtung →</span>
        </div>
        <div class="platform-sectors">
          <div class="sector" v-for="sector in ['F', 'E', 'D', 'C', 'B', 'A']" :key="sector">
            {{ sector }}
          </div>
        </div>
      </div>
      
      <div class="coaches-container">
        <div class="loco-nose">
          <img v-if="getLeftNoseImage()" :src="getLeftNoseImage()" alt="Left Nose" class="nose-image" />
        </div>

        <div
          v-for="coach in coaches"
          :key="coach.number"
          class="coach-item"
          :class="{ 'coach-disabled': !coach.available || coach.load >= 100 }"
          @click="openSeatSelection(coach)"
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
          
          <div class="coach-services">
            <div class="service-row" v-if="coach.wifi">
              <span class="service-icon">📶</span>
              <span class="service-indicator" :class="getWifiClass(coach.wifi)"></span>
            </div>
            <div class="service-row" v-if="coach.toilet">
              <span class="service-icon">🚺</span>
              <span class="service-status" :class="{ 'status-blocked': coach.toilet === 'blocked' }">
                {{ coach.toilet === 'available' ? '✓' : '✗' }}
              </span>
            </div>
            <div class="service-row" v-if="coach.powerOutlets !== undefined">
              <span class="service-icon">🔌</span>
              <span class="service-value">{{ coach.powerOutlets }}%</span>
            </div>
          </div>
          
          <div class="coach-load">
            <v-progress-linear 
              :model-value="coach.load" 
              height="8" 
              rounded 
              :color="getLoadColor(coach.load)"
              bg-color="#e0e0e0"
              bg-opacity="1"
            />
            <span class="load-text">{{ coach.load }}%</span>
          </div>
        </div>

        <div class="loco-nose">
          <img v-if="getRightNoseImage()" :src="getRightNoseImage()" alt="Right Nose" class="nose-image" />
        </div>
      </div>
    </v-card-text>
  </v-card>

  <SeatSelection ref="seatSelectionRef" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SeatSelection from '@/components/SeatSelection.vue'
import regio1 from '@/assets/regio1.png'
import regio2 from '@/assets/regio2.png'
import ice1 from '@/assets/ice1.png'
import ice2 from '@/assets/ice2.png'

const seatSelectionRef = ref(null)

const props = defineProps({
  coaches: {
    type: Array,
    required: true,
    default: () => []
  },
  trainType: {
    type: String,
    required: false,
    default: ''
  }
})

console.log('CoachSequence mounted with trainType:', props.trainType);


const getLoadColor = (load) => {
  if (load >= 70) return '#d93128' // Red for high load
  if (load >= 40) return '#faab23' // Orange for medium load
  return '#33b504' // Green for low load
}

const getWifiClass = (signal) => {
  if (signal === 'good') return 'wifi-good'
  if (signal === 'medium') return 'wifi-medium'
  return 'wifi-poor'
}

const getLeftNoseImage = () => {
  if (props.trainType.startsWith('RE')) return regio1
  if (props.trainType.startsWith('ICE') || props.trainType.startsWith('IC')) return ice1
  return null
}

const getRightNoseImage = () => {
  if (props.trainType.startsWith('RE')) return regio2
  if (props.trainType.startsWith('ICE') || props.trainType.startsWith('IC')) return ice2
  return null
}

const openSeatSelection = (coach) => {
  if (coach.available && coach.load < 100) {
    seatSelectionRef.value?.openCoachSeats(coach)
  }
}

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
  padding: 14px;
  border: 2px solid rgb(217, 46, 40);
  border-radius: 8px;
  background: #f9f9f9;
  min-width: 120px;
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
  font-size: 20px;
  font-weight: 700;
  color: rgb(217, 46, 40);
}

.coach-type {
  font-size: 11px;
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

.coach-services {
  display: flex;
  flex-direction: row;
  gap: 8px;
  width: 100%;
  padding: 4px 0;
  justify-content: center;
  align-items: center;
}

.service-row {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  gap: 2px;
}

.service-icon {
  font-size: 12px;
}

.service-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.wifi-good {
  background: #33b504;
}

.wifi-medium {
  background: #faab23;
}

.wifi-poor {
  background: #d93128;
}

.service-status {
  font-size: 11px;
  font-weight: 700;
  color: #33b504;
}

.service-status.status-blocked {
  color: #d93128;
}

.service-value {
  font-size: 10px;
  font-weight: 600;
  color: #666;
}

.coach-load {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.load-text {
  font-size: 12px;
  color: #666;
  font-weight: 600;
}

/* Nose shapes at both ends */
.loco-nose {
  display: flex;
  align-items: stretch;
  justify-content: center;
  flex: 0 0 150px;
  flex-shrink: 0;
  margin: 0 6px;
}
.loco-nose svg { width: 100%; height: 100%; }
.loco-nose .nose-image { width: 100%; height: 100%; object-fit: contain; }

/* Mobile responsive adjustments */
@media (max-width: 768px) {
  .platform-track-label {
    flex-direction: column;
    gap: 4px;
    align-items: flex-start;
  }

  .track-number {
    font-size: 11px;
    padding: 3px 8px;
  }

  .direction-label {
    font-size: 10px;
  }

  .platform-sectors {
    padding: 3px 4px;
    gap: 0px;
  }

  .sector {
    width: 22px;
    height: 22px;
    min-width: 22px;
    max-width: 22px;
    font-size: 10px;
  }

  .coaches-container {
    gap: 8px;
  }

  .coach-item {
    min-width: 100px;
    padding: 10px;
    gap: 6px;
  }

  .coach-header {
    gap: 1px;
  }

  .coach-number {
    font-size: 16px;
    line-height: 1;
  }

  .coach-type {
    font-size: 9px;
    line-height: 1;
    margin-left: 4px;
  }

  .amenity-badge {
    font-size: 12px;
  }

  .service-icon {
    font-size: 10px;
  }

  .service-row {
    font-size: 9px;
    gap: 1px;
  }

  .load-text {
    font-size: 10px;
  }

  .loco-nose {
    flex: 0 0 100px;
  }
}

@media (max-width: 480px) {
  .coach-sequence-card {
    margin: 8px 0;
  }

  .platform-track-label {
    flex-direction: column;
    gap: 3px;
    align-items: flex-start;
    margin-bottom: 4px;
  }

  .track-number {
    font-size: 10px;
    padding: 2px 6px;
    line-height: 1;
  }

  .direction-label {
    font-size: 9px;
    line-height: 1;
  }

  .platform-sectors {
    padding: 2px 3px;
    gap: 0px;
    margin-bottom: 8px;
  }

  .sector {
    width: 20px;
    height: 20px;
    min-width: 20px;
    max-width: 20px;
    font-size: 9px;
    line-height: 1;
  }

  .coaches-container {
    gap: 6px;
    padding: 4px 0;
  }

  .coach-item {
    min-width: 85px;
    padding: 8px;
    gap: 4px;
    border-width: 1px;
  }

  .coach-header {
    gap: 0px;
  }

  .coach-number {
    font-size: 14px;
    line-height: 1.1;
  }

  .coach-type {
    font-size: 8px;
    line-height: 1;
    margin-left: 10px;
  }

  .coach-amenities {
    min-height: 18px;
    gap: 2px;
  }

  .amenity-badge {
    font-size: 11px;
  }

  .coach-services {
    gap: 3px;
    padding: 2px 0;
  }

  .service-icon {
    font-size: 9px;
  }

  .service-indicator {
    width: 6px;
    height: 6px;
  }

  .service-value {
    font-size: 8px;
  }

  .load-text {
    font-size: 9px;
    line-height: 1;
  }

  .loco-nose {
    flex: 0 0 80px;
    margin: 0 4px;
  }
}
</style>
