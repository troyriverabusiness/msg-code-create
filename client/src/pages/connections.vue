<template>
    <v-row class="ma-1">
      <v-col cols="12">
        
      </v-col>
      <v-col cols="12">
        <v-expansion-panels>
          <v-expansion-panel v-for="item in items" :key="item.name">
            <template #title>
              <v-row no-gutters align="center" class="w-100">
                <v-col cols="1" class="text-left pl-2">
                  <div class="line-badge">{{ item.line }}</div>
                </v-col>
                <v-col cols="8">
                  <div class="route-text">
                    {{ item.route }}
                  </div>
                  <div class="destination-text">
                    {{ item.destination }}
                  </div>
                </v-col>
                <v-col cols="3" class="text-right pr-2">
                  <div class="time-scheduled">{{ item.scheduled_time }}</div>
                  <div class="time-actual">{{ item.actual_time }}</div>
                </v-col>
              </v-row>
            </template>
            <v-expansion-panel-text>
              <CoachSequence :coaches="item.coaches"/>
              <div class="panel-content">
                <p>Weitere Informationen und Optionen hier...</p>
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

const items = ref([
  {
    name: 'RE 54',
    line: 'RE 54',
    route: 'Frankfurt (Main) Süd - Hanau Hbf - Aschaffenburg Hbf',
    destination: 'Würzburg Hbf',
    scheduled_time: '23:30',
    actual_time: '23:30',
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
  },
]
  },
  {
    name: 'ICE 690',
    line: 'ICE 690',
    route: 'Frankfurt Hbf - Mannheim Hbf - Karlsruhe Hbf',
    destination: 'Munich Hbf',
    scheduled_time: '10:05',
    actual_time: '10:10'
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
  font-size: 20px;
  font-weight: 700;
  color: rgb(217, 46, 40);
  letter-spacing: 0.5px;
}

.route-text {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.destination-text {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.time-scheduled {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.time-actual {
  font-size: 13px;
  color: #7ed321;
  margin-top: 8px;
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
</style>
