<template>
    <v-row class="ma-1">
      <v-col cols="12">
        
      </v-col>
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
import { ref } from 'vue'
import CoachSequence from '@/components/CoachSequence.vue'

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
  
  // Finde den Wagen mit der niedrigsten Auslastung
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

const items = ref([
  {
    name: 'RE 54',
    line: 'RE 54',
    route: 'Frankfurt (Main) Süd - Hanau Hbf - Aschaffenburg Hbf',
    destination: 'Würzburg Hbf',
    start_time: '23:30',
    end_time: '01:45',
    duration: '2h 15min',
    scheduled_time: '23:30',
    actual_time: '23:30',
    stops: [
      { station: 'Frankfurt (Main) Süd', platform: '4', arrival: '23:30', departure: '23:30', delay: 0 },
      { station: 'Hanau Hbf', platform: '3', arrival: '23:52', departure: '23:54', delay: 0 },
      { station: 'Aschaffenburg Hbf', platform: '2', arrival: '00:15', departure: '00:17', delay: 0 },
      { station: 'Würzburg Hbf', platform: '5', arrival: '01:45', departure: '-', delay: 0 }
    ],
    coaches: [
  {
    number: '1',
    type: '1st Class',
    available: true,
    isQuiet: false,
    isFamily: true,
    isBarrierefrei: true,
    hasBikes: false,
    load: 45,
    wifi: 'good',
    toilet: 'available',
    powerOutlets: 85
  },
  {
    number: '2',
    type: '2nd Class',
    available: true,
    isQuiet: true,
    isFamily: false,
    isBarrierefrei: false,
    hasBikes: true,
    load: 60,
    wifi: 'medium',
    toilet: 'blocked',
    powerOutlets: 70
  },
  {
    number: '3',
    type: '2nd Class',
    available: true,
    isQuiet: false,
    isFamily: false,
    isBarrierefrei: true,
    hasBikes: true,
    load: 30,
    wifi: 'good',
    toilet: 'available',
    powerOutlets: 90
  },
  {
    number: '4',
    type: 'Bistro',
    available: false,
    isQuiet: false,
    isFamily: false,
    isBarrierefrei: false,
    hasBikes: false,
    load: 0,
    wifi: 'poor',
    powerOutlets: 50
  },
  {
    number: '5',
    type: '2nd Class',
    available: true,
    isQuiet: false,
    isFamily: false,
    isBarrierefrei: false,
    hasBikes: false,
    load: 75,
    wifi: 'medium',
    toilet: 'available',
    powerOutlets: 65
  },
  {
    number: '6',
    type: '1st Class',
    available: true,
    isQuiet: false,
    isFamily: false,
    isBarrierefrei: true,
    hasBikes: false,
    load: 50,
    wifi: 'good',
    toilet: 'available',
    powerOutlets: 95
  },
]
  },
  {
    name: 'Multi-Segment Journey',
    route: 'Frankfurt Hbf - Würzburg Hbf - München Hbf',
    destination: 'München Hbf',
    start_time: '09:00',
    end_time: '12:30',
    duration: '3h 30min',
    scheduled_time: '09:00',
    actual_time: '09:00',
    segments: [
      {
        line: 'RE 54',
        stops: [
          { station: 'Frankfurt Hbf', platform: '5', arrival: '09:00', departure: '09:00', delay: 0 },
          { station: 'Hanau Hbf', platform: '3', arrival: '09:22', departure: '09:24', delay: 0 },
          { station: 'Aschaffenburg Hbf', platform: '2', arrival: '09:45', departure: '09:47', delay: 0 },
          { station: 'Würzburg Hbf', platform: '4', arrival: '10:15', departure: '-', delay: 0 }
        ],
        coaches: [
          { number: '1', type: '2nd Class', available: true, isQuiet: false, isFamily: true, isBarrierefrei: true, hasBikes: false, load: 35, wifi: 'good', toilet: 'available', powerOutlets: 80 },
          { number: '2', type: '2nd Class', available: true, isQuiet: true, isFamily: false, isBarrierefrei: false, hasBikes: true, load: 50, wifi: 'medium', toilet: 'blocked', powerOutlets: 65 },
          { number: '3', type: '1st Class', available: true, isQuiet: false, isFamily: false, isBarrierefrei: true, hasBikes: false, load: 25, wifi: 'good', toilet: 'available', powerOutlets: 90 }
        ],
        transfer: {
          station: 'Würzburg Hbf',
          minutes: 8,
          platformChange: 'Gleis 4 → Gleis 7',
          distance: 200
        }
      },
      {
        line: 'ICE 590',
        stops: [
          { station: 'Würzburg Hbf', platform: '7', arrival: '10:23', departure: '10:23', delay: 0 },
          { station: 'Nürnberg Hbf', platform: '12', arrival: '11:15', departure: '11:18', delay: 0 },
          { station: 'Ingolstadt Hbf', platform: '3', arrival: '11:50', departure: '11:52', delay: 0 },
          { station: 'München Hbf', platform: '18', arrival: '12:30', departure: '-', delay: 0 }
        ],
        coaches: [
          { number: '1', type: '1st Class', available: true, isQuiet: true, isFamily: false, isBarrierefrei: true, hasBikes: false, load: 40, wifi: 'good', toilet: 'available', powerOutlets: 90 },
          { number: '2', type: '2nd Class', available: true, isQuiet: false, isFamily: true, isBarrierefrei: true, hasBikes: false, load: 65, wifi: 'good', toilet: 'available', powerOutlets: 85 },
          { number: '3', type: '2nd Class', available: true, isQuiet: false, isFamily: false, isBarrierefrei: false, hasBikes: true, load: 55, wifi: 'medium', toilet: 'blocked', powerOutlets: 70 },
          { number: '4', type: 'Bistro', available: true, isQuiet: false, isFamily: false, isBarrierefrei: true, hasBikes: false, load: 0, wifi: 'good', toilet: 'available', powerOutlets: 50 }
        ]
      }
    ]
  },
  {
    name: 'ICE 690',
    line: 'ICE 690',
    route: 'Frankfurt Hbf - Mannheim Hbf - Karlsruhe Hbf',
    destination: 'Munich Hbf',
    start_time: '10:05',
    end_time: '13:35',
    duration: '3h 30min',
    scheduled_time: '10:05',
    actual_time: '10:10',
    transfer: {
      station: 'Frankfurt Hbf',
      minutes: 12,
      platformChange: 'Gleis 4 → Gleis 7',
      distance: 150
    },
    stops: [
      { station: 'Frankfurt Hbf', platform: '7', arrival: '10:05', departure: '10:05', delay: 0 },
      { station: 'Mannheim Hbf', platform: '5', arrival: '10:35', departure: '10:38', delay: 3 },
      { station: 'Karlsruhe Hbf', platform: '4', arrival: '11:05', departure: '11:08', delay: 5 },
      { station: 'Stuttgart Hbf', platform: '16', arrival: '11:50', departure: '11:55', delay: 5 },
      { station: 'Munich Hbf', platform: '18', arrival: '13:35', departure: '-', delay: 5 }
      ]
  }
])

    const mockTrainRouteOption = {
      
  // 🚂 Die Route Option (The "Card") - Kurzübersicht für Listenansicht
  trip_id: "ICE690_F-H_20251205",
  line_name: "ICE 690",
  type: "ICE", // Für visuelle Darstellung (Icon)
  
  times: {
    scheduled_departure: "10:00",
    real_time_departure: "10:05",
    delay_minutes: 5,
    scheduled_arrival: "11:30",
    real_time_arrival: "11:35"
  },
  
  platform: {
    name: "Gleis 4",
    // Info aus pathways.txt (oder ähnlicher Quelle)
    accessibility: "Barrierefreier Zugang (Aufzug/Rampe)" 
  },
  
  // Simulationswert, z.B. basierend auf Wochentag/Uhrzeit
  occupancy: "high", // Mögliche Werte: 'low', 'medium', 'high', 'full'
  
  // 🏢 Stationsdetails (The "Context") - Zusätzliche Infos
  station_details: {
    name: "Frankfurt (Main) Hbf",
    
    // Abgeleitet aus pathways.txt
    facilities: [
      { name: "Aufzug Gleis 4", status: "operational" },
      { name: "Rolltreppe Gleis 4", status: "operational" },
      { name: "Information", status: "operational" }
    ],
    
    // Abgeleitet aus NeTEx/GTFS
    entrances: [
      { name: "Haupteingang (Süden)", accessibility: "Barrierefrei" },
      { name: "Eingang Nordseite", accessibility: "Eingeschränkte Barrierefreiheit" }
    ]
  },
  
  // ⚠️ Echtzeit-Status (The "Ticker") - Wichtige Meldungen (SIRI)
  real_time_status: {
    is_disrupted: true, // Ist die Fahrt betroffen?
    
    // Abgeleitet aus SIRI oder anderen Echtzeit-Quellen
    messages: [
      { 
        severity: "critical", 
        text: "Zug fällt wegen technischer Störung aus.",
        source: "SIRI"
      }
    ],
    
    // Logik für Alternativen bei Ausfall
    alternatives: [
      {
        line_name: "IC 2018",
        departure: "10:20",
        platform: "Gleis 5"
      },
      {
        line_name: "RB 82 (via Offenbach)",
        departure: "10:15",
        platform: "Gleis 8"
      }
    ]
  }
};
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
