<template>
    <v-row class="ma-1">
      <v-col cols="12">
        <v-expansion-panels>
          <v-expansion-panel v-for="item in items" :key="item.name">
            <template #title>
              <v-row no-gutters align="center" class="w-100">
                <v-col cols="1.5" md="1" class="text-left pl-0">
                  <div class="line-badge-wrapper">
                    <div class="line-badge">{{ item.segments ? item.segments[0].line : item.line }}</div>
                    <div v-if="item.segments && item.segments.length > 1" class="line-badge-secondary">
                      {{ item.segments[item.segments.length - 1].line }}
                    </div>
                  </div>
                </v-col>
                <v-col cols="8">
                  <div class="route-text">
                    {{ item.route }}
                  </div>
                  <div class="destination-text">
                    {{ item.destination }}
                  </div>
                  <div class="journey-info" v-if="item.start_time && item.end_time && item.duration">
                    {{ item.start_time }} → {{ item.end_time }} • {{ item.duration }}
                    <span v-if="item.segments && item.segments.length > 1" class="transfer-count">
                      • {{ item.segments.length - 1 }}x Umstieg
                    </span>
                  </div>

                </v-col>
                <v-col cols="3" class="text-right pr-2">
                  <div class="time-scheduled">{{ item.scheduled_time }}</div>
                  <div class="time-actual" :class="{ 'time-delayed': getDelay(item) > 0 }">
                    {{ item.actual_time }}
                    <span v-if="getDelay(item) > 0"> (+{{ getDelay(item) }} min)</span>
                  </div>
                </v-col>
              </v-row>
            </template>
            <v-expansion-panel-text>
              <!-- Render each segment (train) -->
              <template v-if="item.segments && item.segments.length > 0">
                <div v-for="(segment, index) in item.segments" :key="index">
                  
                  <!-- Zwischenstops -->
                  <div class="stops-section" v-if="segment.stops && segment.stops.length">
                    <h4 class="stops-title">{{ segment.line }} - Zwischenstops</h4>
                    <div class="stops-timeline">
                      <div v-for="(stop, stopIndex) in segment.stops" :key="stop.station" class="timeline-stop">
                        <div class="timeline-marker">
                          <div class="timeline-dot"></div>
                          <div class="timeline-line" v-if="stopIndex < segment.stops.length - 1"></div>
                        </div>
                        <div class="timeline-content">
                          <div class="stop-header">
                            <div class="stop-station">{{ stop.station }}</div>
                            <div class="stop-platform" v-if="stop.platform">Gl. {{ stop.platform }}</div>
                          </div>
                          <div class="stop-times">
                            <span class="stop-time">An: {{ stop.arrival }}</span>
                            <span class="stop-separator">•</span>
                            <span class="stop-time">Ab: {{ stop.departure }}</span>
                            <span class="stop-delay" v-if="stop.delay">+{{ stop.delay }} min</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Transfer Information (only between segments) -->
                  <div class="transfer-section" v-if="index < item.segments.length - 1 && segment.transfer">
                    <div class="transfer-indicator">
                      <div class="transfer-icon">🔄</div>
                      <div class="transfer-details">
                        <div class="transfer-station">Umstieg in {{ segment.transfer.station }}</div>
                        <div class="transfer-info">
                          <span class="transfer-time" :class="getTransferTimeClass(segment.transfer.minutes)">
                            {{ segment.transfer.minutes }} min
                          </span>
                          <span class="transfer-separator">•</span>
                          <span class="transfer-platforms">{{ segment.transfer.platformChange }}</span>
                          <span v-if="segment.transfer.distance" class="transfer-distance">
                            • ca. {{ segment.transfer.distance }}m
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <CoachSequence :coaches="segment.coaches" :train-type="segment.line"/>
                </div>
              </template>

              <!-- Fallback for old structure (single train) -->
              <!-- Fallback for old structure (single train) -->
              <template v-else>
                <!-- Zwischenstops -->
                <div class="stops-section" v-if="item.stops && item.stops.length">
                  <h4 class="stops-title">Zwischenstops</h4>
                  <div class="stops-timeline">
                    <div v-for="(stop, index) in item.stops" :key="stop.station" class="timeline-stop">
                      <div class="timeline-marker">
                        <div class="timeline-dot"></div>
                        <div class="timeline-line" v-if="index < item.stops.length - 1"></div>
                      </div>
                      <div class="timeline-content">
                        <div class="stop-header">
                          <div class="stop-station">{{ stop.station }}</div>
                          <div class="stop-platform" v-if="stop.platform">Gl. {{ stop.platform }}</div>
                        </div>
                        <div class="stop-times">
                          <span class="stop-time">An: {{ stop.arrival }}</span>
                          <span class="stop-separator">•</span>
                          <span class="stop-time">Ab: {{ stop.departure }}</span>
                          <span class="stop-delay" v-if="stop.delay">+{{ stop.delay }} min</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <CoachSequence :coaches="item.coaches" :train-type="item.line"/>
              </template>

              <!-- AI Coach Recommendation -->
              <div class="ai-recommendation-section">
                <div class="recommendation-header">
                  <span class="ai-icon">✨</span>
                  <h4 class="recommendation-title">Empfehlung</h4>
                </div>
                <div class="recommendation-content">
                  <p class="recommendation-text">{{ getCoachRecommendation(item.coaches) }}</p>
                </div>
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
</template>

<script setup>
import { ref, computed } from 'vue'
import CoachSequence from '@/components/CoachSequence.vue'
import { useBackendCalls } from '@/stores/backendCalls'

const backendCallsStore = useBackendCalls()

// Transform connections from store to the format expected by the template
const items = computed(() => {
  return backendCallsStore.connections.map(connection => {
    const firstLeg = connection.legs[0]
    const lastLeg = connection.legs[connection.legs.length - 1]
    
    // Build segments from legs
    const segments = connection.legs.map((leg, index) => {
      // Build stops array: origin + intermediate stops (path) + destination
      const stops = [
        {
          station: leg.origin.name,
          platform: String(leg.train.platform),
          arrival: '-',
          departure: formatTime(leg.departureTime),
          delay: 0
        }
      ];
      
      // Add intermediate stops from path
      if (leg.train.path && leg.train.path.length > 0) {
        leg.train.path.forEach(pathStop => {
          stops.push({
            station: pathStop.station.name,
            platform: String(leg.train.platform),
            arrival: formatTime(pathStop.arrivalTime),
            departure: formatTime(pathStop.departureTime),
            delay: 0
          });
        });
      }
      
      // Add destination stop
      stops.push({
        station: leg.destination.name,
        platform: String(leg.train.platform),
        arrival: formatTime(leg.arrivalTime),
        departure: '-',
        delay: 0
      });
      
      return {
        line: leg.train.name,
        stops: stops,
        coaches: leg.train.wagons.map((wagon, i) => {
          const load = Math.floor(Math.random() * 100) + 1;
          return {
            number: String(wagon),
            type: i === 0 ? '1st Class' : '2nd Class',
            available: load < 100,
            isQuiet: Math.random() > 0.7,
            isFamily: Math.random() > 0.8,
            isBarrierefrei: Math.random() > 0.6,
            hasBikes: Math.random() > 0.7,
            load: load,
            wifi: ['good', 'medium', 'poor'][Math.floor(Math.random() * 3)],
            toilet: ['available', 'blocked', 'unavailable'][Math.floor(Math.random() * 3)],
            powerOutlets: Math.floor(Math.random() * 50) + 50
          };
        }),
        transfer: index < connection.legs.length - 1 ? {
          station: leg.destination.name,
          minutes: calculateTransferTime(leg.arrivalTime, connection.legs[index + 1].departureTime),
          platformChange: `Gl. ${leg.train.platform} → Gl. ${connection.legs[index + 1].train.platform}`
        } : null
      };
    });

    return {
      id: connection.id,
      name: firstLeg.train.name,
      line: firstLeg.train.name,
      route: `${connection.startStation.name} - ${connection.endStation.name}`,
      destination: connection.endStation.name,
      start_time: formatTime(firstLeg.departureTime),
      end_time: formatTime(lastLeg.arrivalTime),
      duration: formatDuration(connection.totalTime),
      scheduled_time: formatTime(firstLeg.departureTime),
      actual_time: formatTime(firstLeg.departureTime),
      transfers: connection.transfers,
      segments: segments,
      stops: [],
      coaches: segments[0]?.coaches || []
    }
  })
})

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  return timeStr.substring(0, 5)
}

const formatDuration = (minutes) => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}h ${mins}min`
}

const calculateTransferTime = (arrivalTime, departureTime) => {
  if (!arrivalTime || !departureTime) return 0
  const [arrH, arrM] = arrivalTime.split(':').map(Number)
  const [depH, depM] = departureTime.split(':').map(Number)
  return (depH * 60 + depM) - (arrH * 60 + arrM)
}

const getDelay = (item) => {
  if (!item.scheduled_time || !item.actual_time) return 0
  
  const parseTime = (timeStr) => {
    const [hours, minutes] = timeStr.split(':').map(Number)
    return hours * 60 + minutes
  }
  
  const scheduledMinutes = parseTime(item.scheduled_time)
  const actualMinutes = parseTime(item.actual_time)
  
  return actualMinutes - scheduledMinutes
}

const getDisplayLine = (item) => {
  if (item.segments && item.segments.length > 1) {
    return item.segments.map(s => s.line).join(' + ')
  }
  return item.line
}

const getTransferTimeClass = (minutes) => {
  if (minutes < 5) return 'transfer-critical'
  if (minutes < 10) return 'transfer-tight'
  return 'transfer-comfortable'
}

const getCoachRecommendation = (coaches) => {
  if (!coaches || coaches.length === 0) return 'Keine Wagen verfügbar'
  
  let bestCoach = coaches[0]
  let lowestLoad = coaches[0].load
  
  for (let coach of coaches) {
    if (coach.available && coach.load < lowestLoad) {
      bestCoach = coach
      lowestLoad = coach.load
    }
  }
  
  // Generiere KI-Vorschlag
  let suggestion = `💡 Wähle Wagen ${bestCoach.number}`
  
  if (bestCoach.load < 30) {
    suggestion += ` für eine entspannte Fahrt - sehr wenig Auslastung (${bestCoach.load}%)`
  } else if (bestCoach.load < 50) {
    suggestion += ` - gute Verfügbarkeit mit ${bestCoach.load}% Auslastung`
  } else {
    suggestion += ` - beste verfügbare Option mit ${bestCoach.load}% Auslastung`
  }
  
  const features = []
  if (bestCoach.isQuiet) features.push('🔇 Ruhebereich')
  if (bestCoach.isFamily) features.push('👨‍👩‍👧 Familienbereich')
  if (bestCoach.isBarrierefrei) features.push('♿ Barrierefrei')
  if (bestCoach.hasBikes) features.push('🚲 Fahrradstellplätze')
  if (bestCoach.wifi === 'good') features.push('📶 Gutes WLAN')
  if (bestCoach.toilet === 'available') features.push('🚺 Toilette verfügbar')
  if (bestCoach.powerOutlets > 70) features.push('🔌 Viele Steckdosen')
  
  if (features.length > 0) {
    suggestion += `. Ausstattung: ${features.join(', ')}`
  }
  
  return suggestion
}
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

.route-text {
  font-size: 15px;
  color: #666;
  margin-bottom: 4px;
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

.panel-content p {
  margin: 8px 0;
  color: #333;
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
