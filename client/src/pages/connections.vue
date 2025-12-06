<template>
  <v-container>
    <!-- Search Form -->
    <v-card class="mb-4 pa-4" elevation="2">
      <v-row>
        <v-col cols="12" md="4">
          <v-text-field
            v-model="search.origin"
            label="Start Station"
            prepend-inner-icon="mdi-train"
            variant="outlined"
            hide-details
          ></v-text-field>
        </v-col>
        <v-col cols="12" md="4">
          <v-text-field
            v-model="search.destination"
            label="Destination"
            prepend-inner-icon="mdi-flag-checkered"
            variant="outlined"
            hide-details
          ></v-text-field>
        </v-col>
        <v-col cols="12" md="2">
          <v-text-field
            v-model="search.time"
            label="Time (HH:MM)"
            type="time"
            variant="outlined"
            hide-details
          ></v-text-field>
        </v-col>
        <v-col cols="12" md="2" class="d-flex align-center">
          <v-btn
            color="primary"
            block
            height="56"
            :loading="store.loading"
            @click="doSearch"
          >
            Search
          </v-btn>
        </v-col>
      </v-row>
    </v-card>

    <!-- Error Alert -->
    <v-alert
      v-if="store.error"
      type="error"
      title="Error"
      class="mb-4"
      closable
    >
      {{ store.error }}
    </v-alert>

    <!-- Results List -->
    <v-row v-if="store.connections.length > 0">
      <v-col cols="12">
        <v-expansion-panels>
          <v-expansion-panel v-for="journey in store.connections" :key="journey.id">
            <template #title>
              <v-row no-gutters align="center" class="w-100">
                <!-- Line / Badge -->
                <v-col cols="2" sm="1" class="text-left pl-2">
                  <div class="line-badge-wrapper">
                    <div class="line-badge">
                      {{ getJourneyLabel(journey) }}
                    </div>
                    <!-- Optional: Secondary badge if multiple trains? kept simple for now -->
                  </div>
                  <div class="transfers-badge" v-if="journey.transfers > 0">
                    {{ journey.transfers }} Transfer(s)
                  </div>
                </v-col>
                
                <!-- Route Info -->
                <v-col cols="7" sm="8">
                  <div class="route-text">
                    {{ formatTime(journey.legs[0].departureTime) }} • {{ journey.startStation.name }}
                  </div>
                  <div class="destination-text">
                    → {{ journey.endStation.name }}
                  </div>
                  <div class="caption text-grey">
                     Duration: {{ formatDuration(journey.totalTime) }}
                  </div>
                  <div class="journey-info">
                    {{ formatTime(journey.legs[0].departureTime) }} → {{ formatTime(journey.legs[journey.legs.length-1].arrivalTime) }}
                  </div>

                </v-col>
                
                <!-- Times -->
                <v-col cols="3" class="text-right pr-2">
                  <div class="time-scheduled">
                    {{ formatTime(journey.legs[journey.legs.length-1].arrivalTime) }}
                  </div>
                  <!-- Realtime data not yet in Journey model, hiding actual time for now -->
                  <!-- <div class="time-actual" :class="{ 'time-delayed': getDelay(journey) > 0 }">
                    {{ journey.actual_time }}
                  </div> -->
                </v-col>
              </v-row>
            </template>
            
            <v-expansion-panel-text>
              <div class="panel-content">
                <!-- Iterate over Legs as Segments -->
                <div v-for="(leg, index) in journey.legs" :key="index">
                  
                  <!-- Train/Leg Header -->
                  <div class="stops-section">
                    <h4 class="stops-title">
                      {{ leg.train.name }} ({{ leg.train.trainNumber }})
                      <span class="text-caption text-grey ml-2">
                        {{ leg.origin.name }} → {{ leg.destination.name }}
                      </span>
                    </h4>

                    <!-- Intermediate Stops (Path) -->
                    <!-- The backend 'train.path' is a list of Stations. -->
                    <div class="stops-timeline" v-if="leg.train.path && leg.train.path.length > 0">
                      <div v-for="(stop, stopIndex) in leg.train.path" :key="stopIndex" class="timeline-stop">
                        <div class="timeline-marker">
                          <div class="timeline-dot"></div>
                          <div class="timeline-line" v-if="stopIndex < leg.train.path.length - 1"></div>
                        </div>
                        <div class="timeline-content">
                          <div class="stop-header">
                            <div class="stop-station">{{ stop.name }}</div>
                            <!-- Platform not yet in Station model for path -->
                          </div>
                          <!-- Arrival/Departure times not yet in simplified Station model in path -->
                        </div>
                      </div>
                    </div>
                    <div v-else class="text-grey text-caption font-italic">
                      (Intermediate stops data not available)
                    </div>
                  </div>

                  <!-- Transfer Information (only between segments) -->
                  <div class="transfer-section" v-if="index < journey.legs.length - 1">
                    <div class="transfer-indicator">
                      <div class="transfer-icon">🔄</div>
                      <div class="transfer-details">
                        <div class="transfer-station">Umstieg in {{ leg.destination.name }}</div>
                        <div class="transfer-info">
                           <!-- Calculate transfer time if possible, or just show text -->
                           Transfer
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Coach Sequence -->
                  <!-- 
                       Backend 'wagons' is List[int] (load percentages). 
                       Frontend 'CoachSequence' expects complex objects.
                       We will construct dummy coach objects from the load data to visualize it.
                  -->
                  <CoachSequence 
                    v-if="leg.train.wagons && leg.train.wagons.length > 0"
                    :coaches="mapWagonsToCoaches(leg.train.wagons)" 
                    :train-type="leg.train.name"
                  />
                </div>

                <!-- AI Coach Recommendation (Global for the journey or per leg? Frontend had it per segment mostly) -->
                 <!-- TODO: Implement Recommendation based on aggregated load -->
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
    
    <v-sheet v-else-if="!store.loading && hasSearched" class="pa-4 text-center text-grey">
      No connections found.
    </v-sheet>
  </v-container>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useBackendCalls } from '@/stores/backendCalls'
import CoachSequence from '@/components/CoachSequence.vue'
import NoseBadge from '@/components/NoseBadge.vue'

const store = useBackendCalls()
const hasSearched = ref(false)

const search = reactive({
  origin: 'Frankfurt (Main) Hbf',
  destination: 'München Hbf',
  time: '08:00'
})

async function doSearch() {
  hasSearched.value = true
  const today = new Date().toISOString().split('T')[0]
  const isoDate = `${today}T${search.time}:00`
  
  await store.fetchConnections(search.origin, search.destination, isoDate)
}

function getJourneyLabel(journey) {
  if (!journey.legs || journey.legs.length === 0) return '??'
  // Return first train name e.g. "ICE"
  return journey.legs[0].train.name.split(' ')[0]
}

function formatTime(isoString) {
  if (!isoString) return ''
  // Expecting ISO string or similar. simplified:
  const parts = isoString.split('T')
  const timePart = parts.length > 1 ? parts[1] : parts[0]
  return timePart.substring(0, 5) // HH:MM
}

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return `${h}h ${m}m`
}

// Helper to map the simple backend [load_int, load_int] to the frontend's expected structure
function mapWagonsToCoaches(wagonLoads) {
  return wagonLoads.map((load, idx) => ({
    number: (idx + 1).toString(),
    type: idx === 0 ? '1st Class' : '2nd Class', // Mock type
    available: true,
    isQuiet: false,
    isFamily: false,
    isBarrierefrei: idx === 0, // Mock
    hasBikes: idx === wagonLoads.length - 1, // Mock
    load: load,
    wifi: 'good',
    toilet: 'available',
    powerOutlets: 80
  }))
}

/*
// Legacy/Unused helpers from frontend (kept for reference if we enhance backend data)
const getDelay = (item) => { ... }
const getCoachRecommendation = (coaches) => { ... }
*/
</script>

<style scoped>
.line-badge {
  font-size: 24px;
  font-weight: 700;
  color: rgb(217, 46, 40);
  letter-spacing: 0.5px;
  padding: 0;
  margin: 0;
}

.line-badge-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.line-badge-secondary {
  font-size: 12px;
  font-weight: 600;
  color: #999;
  letter-spacing: 0.5px;
}

.transfers-badge {
  font-size: 11px;
  color: #666;
  background-color: #f0f0f0;
  border-radius: 4px;
  padding: 2px 4px;
  display: inline-block;
  margin-top: 4px;
}

.route-text {
  font-size: 15px;
  color: #666;
  margin-bottom: 2px;
}

.destination-text {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.journey-info {
  font-size: 13px;
  color: #666;
  margin-top: 4px;
}

.transfer-count {
  color: #ff9800;
  font-weight: 600;
}

.time-scheduled {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-right: 8px;
  display: block;
}

.time-actual {
  font-size: 15px;
  color: #7ed321;
  margin-top: 8px;
  margin-right: 8px;
  display: block;
}

.time-actual.time-delayed {
  color: #d93128;
  font-weight: 600;
}

.panel-content {
  padding: 12px 0;
}

.w-100 {
  width: 100%;
}

/* Stops section */
.stops-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
}

.stops-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.stops-timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.timeline-stop {
  display: flex;
  gap: 12px;
  position: relative;
}

.timeline-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgb(217, 46, 40);
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px rgb(217, 46, 40);
  z-index: 2;
  flex-shrink: 0;
}

.timeline-line {
  width: 2px;
  flex: 1;
  background: #ddd;
  min-height: 40px;
}

.timeline-content {
  flex: 1;
  padding-bottom: 16px;
}

.stop-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.stop-station {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.stop-platform {
  font-size: 12px;
  color: #fff;
  background: #003366;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.stop-times {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.stop-time {
  font-weight: 500;
}

.stop-separator {
  color: #999;
}

.stop-delay {
  color: #d93128;
  font-weight: 600;
  margin-left: 4px;
}

/* AI Recommendation Section */
.ai-recommendation-section {
  margin: 24px 0 0 0;
  padding: 16px 20px;
  background: #ECFFE8;
  border-left: 4px solid #7ed321;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.recommendation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.ai-icon {
  font-size: 20px;
}

.recommendation-title {
  font-size: 16px;
  font-weight: 700;
  color: #000000;
  margin: 0;
}

.recommendation-content {
  padding: 0;
}

.recommendation-text {
  font-size: 14px;
  color: #000000;
  margin: 0;
  line-height: 1.6;
  font-weight: 500;
}

/* Transfer Section */
.transfer-section {
  margin: 20px 0;
  padding: 0;
}

.transfer-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: linear-gradient(135deg, #fff8e1 0%, #ffe0b2 100%);
  border-left: 4px solid #ff9800;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.transfer-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.transfer-details {
  flex: 1;
}

.transfer-station {
  font-size: 15px;
  font-weight: 700;
  color: #e65100;
  margin-bottom: 4px;
}

.transfer-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
}

.transfer-time {
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}

.transfer-comfortable {
  background: #c8e6c9;
  color: #2e7d32;
}

.transfer-tight {
  background: #ffe0b2;
  color: #e65100;
}

.transfer-critical {
  background: #ffcdd2;
  color: #c62828;
  animation: blink 1.5s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.transfer-separator {
  color: #999;
}

.transfer-platforms {
  font-weight: 600;
  color: #003366;
}

.transfer-distance {
  color: #666;
}
</style>
