<template>
  <div class="db-page">
    <v-container class="db-container">
      <v-row justify="center">
        <v-col cols="12" md="10" lg="8">
          <div class="db-card">
            <h1 class="db-title">Reiseauskunft</h1>

            <div class="db-search-box">
              <v-text-field
                v-model="prompt.text"
                append-inner-icon="mdi-send"
                label="Enter a prompt to search for train connections..."
                variant="outlined"
                hide-details
                density="comfortable"
                class="db-input"
                @click:append-inner="send"
              />
            </div>

            <v-expansion-panels class="db-panels" flat>
              <v-expansion-panel>
                <v-expansion-panel-title class="db-panel-title">
                  <v-icon icon="mdi-tune" size="small" class="mr-2" />
                  Manual Input
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <v-row class="mb-4">
                    <v-col cols="12" sm="5">
                      <v-combobox
                        v-model="prompt.manualInput.start"
                        label="Von"
                        variant="outlined"
                        density="comfortable"
                        hide-details
                      />
                    </v-col>
                    <v-col class="d-flex align-center justify-center" cols="12" sm="2">
                      <v-btn icon variant="text" size="small">
                        <v-icon icon="mdi-swap-horizontal" color="#EC0016" />
                      </v-btn>
                    </v-col>
                    <v-col cols="12" sm="5">
                      <v-combobox
                        v-model="prompt.manualInput.destination"
                        label="Nach"
                        variant="outlined"
                        density="comfortable"
                        hide-details
                      />
                    </v-col>
                  </v-row>

                  <v-row class="mb-4">
                    <v-col cols="12" sm="6">
                      <DateTimePicker
                        v-model="prompt.manualInput.departureDate"
                        label="Hinfahrt"
                      />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <DateTimePicker
                        v-model="prompt.manualInput.returnDate"
                        label="Rückfahrt (optional)"
                      />
                    </v-col>
                  </v-row>

                  <v-row>
                    <v-col cols="12" sm="6">
                      <v-select
                        v-model="prompt.manualInput.transportModes"
                        :items="verkehrsmittel"
                        label="Verkehrsmittel"
                        variant="outlined"
                        density="comfortable"
                        multiple
                        hide-details
                      />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-select
                        v-model="prompt.manualInput.transferTime"
                        :items="umstiegszeiten"
                        label="Umstiegszeit"
                        variant="outlined"
                        density="comfortable"
                        hide-details
                      />
                    </v-col>
                  </v-row>

                  <v-row class="mt-4">
                    <v-col cols="12">
                      <v-btn
                        color="#EC0016"
                        size="large"
                        class="db-search-btn"
                        @click="send"
                      >
                        <v-icon icon="mdi-magnify" class="mr-2" />
                        Verbindungen suchen
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import DateTimePicker from '@/components/DateTimePicker.vue'

  const verkehrsmittel = ref(['ICE', 'IC', 'RE', 'RB', 'S-Bahn', 'U-Bahn', 'Tram', 'Bus'])
  const umstiegszeiten = ref(['5 Minuten', '10 Minuten', '15 Minuten', '20 Minuten', '30 Minuten'])

  const prompt = ref({
    text: null,
    manualInput: {
      start: null,
      destination: null,
      transportModes: [],
      transferTime: null,
      departureDate: null,
      returnDate: null,
    },
  })

  async function send () {
    console.log('Sending prompt to backend')
    console.log(prompt.value)
  }

  const mockTrainRouteOption = {
    // 🚂 Die Route Option (The "Card") - Kurzübersicht für Listenansicht
    trip_id: 'ICE690_F-H_20251205',
    line_name: 'ICE 690',
    type: 'ICE', // Für visuelle Darstellung (Icon)

    times: {
      scheduled_departure: '10:00',
      real_time_departure: '10:05',
      delay_minutes: 5,
      scheduled_arrival: '11:30',
      real_time_arrival: '11:35',
    },

    platform: {
      name: 'Gleis 4',
      // Info aus pathways.txt (oder ähnlicher Quelle)
      accessibility: 'Barrierefreier Zugang (Aufzug/Rampe)',
    },

    // Simulationswert, z.B. basierend auf Wochentag/Uhrzeit
    occupancy: 'high', // Mögliche Werte: 'low', 'medium', 'high', 'full'

    // 🏢 Stationsdetails (The "Context") - Zusätzliche Infos
    station_details: {
      name: 'Frankfurt (Main) Hbf',

      // Abgeleitet aus pathways.txt
      facilities: [
        { name: 'Aufzug Gleis 4', status: 'operational' },
        { name: 'Rolltreppe Gleis 4', status: 'operational' },
        { name: 'Information', status: 'operational' },
      ],

      // Abgeleitet aus NeTEx/GTFS
      entrances: [
        { name: 'Haupteingang (Süden)', accessibility: 'Barrierefrei' },
        { name: 'Eingang Nordseite', accessibility: 'Eingeschränkte Barrierefreiheit' },
      ],
    },

    // ⚠️ Echtzeit-Status (The "Ticker") - Wichtige Meldungen (SIRI)
    real_time_status: {
      is_disrupted: true, // Ist die Fahrt betroffen?

      // Abgeleitet aus SIRI oder anderen Echtzeit-Quellen
      messages: [
        {
          severity: 'critical',
          text: 'Zug fällt wegen technischer Störung aus.',
          source: 'SIRI',
        },
      ],

      // Logik für Alternativen bei Ausfall
      alternatives: [
        {
          line_name: 'IC 2018',
          departure: '10:20',
          platform: 'Gleis 5',
        },
        {
          line_name: 'RB 82 (via Offenbach)',
          departure: '10:15',
          platform: 'Gleis 8',
        },
      ],
    },
  }

</script>

<style scoped>
/* DB-inspired styling with characteristic red (#EC0016) and clean layout */
.db-page {
  min-height: 100vh;
  background: #F0F3F5;
  padding: 2rem 1rem;
}

.db-container {
  max-width: 1200px;
}

.db-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.db-title {
  font-size: 2rem;
  font-weight: 700;
  color: #282D37;
  margin-bottom: 1.5rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.db-search-box {
  margin-bottom: 1.5rem;
}

.db-input :deep(.v-field) {
  border-radius: 4px;
  font-size: 1rem;
}

.db-input :deep(.v-field__append-inner) {
  cursor: pointer;
}

.db-input :deep(.v-field__append-inner:hover .v-icon) {
  color: #EC0016 !important;
}

.db-panels {
  background: transparent;
  margin-top: 1rem;
}

.db-panels :deep(.v-expansion-panel) {
  background: transparent;
  box-shadow: none;
  border: none;
}

.db-panels :deep(.v-expansion-panel::before) {
  box-shadow: none;
}

.db-panel-title {
  background: transparent !important;
  padding: 0.75rem 0;
  min-height: auto !important;
  font-weight: 600;
  color: #282D37;
  font-size: 0.95rem;
}

.db-panels :deep(.v-expansion-panel-title__overlay) {
  display: none;
}

.db-panels :deep(.v-expansion-panel-text__wrapper) {
  padding: 1.5rem 0;
}

.db-search-btn {
  width: 100%;
  text-transform: none;
  font-weight: 600;
  letter-spacing: 0.3px;
  font-size: 1rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mt-4 {
  margin-top: 1rem;
}
</style>
