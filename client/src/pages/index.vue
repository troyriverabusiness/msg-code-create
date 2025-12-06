<template>
  <v-row justify="center">
    <v-col cols="10">
      <v-row align="start" justify="space-between">
        <v-text-field
          v-model="prompt.text"
          append-inner-icon="mdi-send"
          label="Enter your prompt on where to go and preferences of how you would like to travel"
          variant="outlined"
          @click:append-inner="send"
        />
      </v-row>
      <v-expansion-panels class="flat-panels" flat>
        <v-expansion-panel title="Manual input">
          <v-expansion-panel-text>
            <v-row class="mb-3">
              <v-col cols="12" sm="5">
                <v-combobox v-model="prompt.manualInput.start" label="Start" />
              </v-col>
              <v-col class="d-flex align-center justify-center" cols="12" sm="1">
                <v-icon icon="mdi-arrow-left-right" />
              </v-col>
              <v-col cols="12" sm="5">
                <v-combobox v-model="prompt.manualInput.destination" label="Destination" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" sm="4">
                <v-select
                  v-model="prompt.manualInput.transportModes"
                  :items="verkehrsmittel"
                  label="Verkehrsmittel"
                  multiple
                />
              </v-col>
              <v-col cols="12" sm="4">
                <v-select
                  v-model="prompt.manualInput.transferTime"
                  :items="umstiegszeiten"
                  label="Umstiegszeit"
                />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" sm="6">
                <DateTimePicker v-model="prompt.manualInput.departureDate" label="Hinfahrt" />
              </v-col>
              <v-col cols="12" sm="6">
                <DateTimePicker v-model="prompt.manualInput.returnDate" label="Rückfahrt (optional)" />
              </v-col>
            </v-row>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-col>
  </v-row>
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
.field-label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.flat-panels {
  background: transparent;
}

.flat-panels :deep(.v-expansion-panel) {
  background: transparent;
  box-shadow: none;
  border: none;
}

.flat-panels :deep(.v-expansion-panel::before) {
  box-shadow: none;
}

.flat-panels :deep(.v-expansion-panel-title) {
  background: transparent;
  padding-left: 0;
  padding-right: 0;
  min-height: auto;
  justify-content: flex-start;
}

.flat-panels :deep(.v-expansion-panel-title__overlay) {
  display: none;
}

.flat-panels :deep(.v-expansion-panel-title__icon) {
  margin-left: 0.5rem;
}

.flat-panels :deep(.v-expansion-panel-text__wrapper) {
  padding-left: 0;
  padding-right: 0;
}
</style>
