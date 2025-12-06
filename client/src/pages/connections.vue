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
                  <div class="line-badge">
                    {{ getJourneyLabel(journey) }}
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
                </v-col>
                
                <!-- Times -->
                <v-col cols="3" class="text-right pr-2">
                  <div class="time-scheduled">
                    {{ formatTime(journey.legs[journey.legs.length-1].arrivalTime) }}
                  </div>
                </v-col>
              </v-row>
            </template>
            
            <v-expansion-panel-text>
              <div class="panel-content">
                <!-- Iterate over Legs -->
                <v-timeline density="compact" align="start">
                  <v-timeline-item
                    v-for="(leg, index) in journey.legs"
                    :key="index"
                    dot-color="primary"
                    size="small"
                  >
                    <div class="mb-2">
                      <div class="font-weight-bold">
                        {{ formatTime(leg.departureTime) }} - {{ leg.origin.name }}
                      </div>
                      <div>
                        <v-icon icon="mdi-train" size="small" class="mr-1"></v-icon>
                        {{ leg.train.name }} ({{ leg.train.trainNumber }})
                        to {{ leg.destination.name }}
                      </div>
                      <div class="text-caption text-grey">
                        Arr: {{ formatTime(leg.arrivalTime) }}
                      </div>
                    </div>
                  </v-timeline-item>
                </v-timeline>
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

const store = useBackendCalls()
const hasSearched = ref(false)

const search = reactive({
  origin: 'Frankfurt (Main) Hbf',
  destination: 'München Hbf',
  time: '08:00'
})

async function doSearch() {
  hasSearched.value = true
  // TODO: Construct full ISO date if needed by backend, currently passing time string mostly
  // Backend expects HH:MM:SS or ISO. Let's send ISO for today with this time.
  const today = new Date().toISOString().split('T')[0]
  const isoDate = `${today}T${search.time}:00`
  
  await store.fetchConnections(search.origin, search.destination, isoDate)
}

function getJourneyLabel(journey) {
  // Use the first train's name (e.g. ICE)
  return journey.legs[0].train.name.split(' ')[0]
}

function formatTime(isoString) {
  // Handles HH:MM:SS
  if (!isoString) return ''
  const parts = isoString.split(':')
  return `${parts[0]}:${parts[1]}`
}

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return `${h}h ${m}m`
}
</script>

<style scoped>
.line-badge {
  font-size: 18px;
  font-weight: 700;
  color: rgb(217, 46, 40);
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
  font-size: 14px;
  color: #666;
  margin-bottom: 2px;
}

.destination-text {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.time-scheduled {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.panel-content {
  padding: 12px 0;
}

.w-100 {
  width: 100%;
}
</style>
