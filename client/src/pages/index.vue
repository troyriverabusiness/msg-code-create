<template>
  <div class="db-page">
    <v-container class="db-container">
      <v-row justify="center">
        <v-col cols="12" md="10" lg="8">
          <div class="db-card">
            <h1 class="db-title">Reiseauskunft</h1>
          <v-row v-if="showPrePlan" justify="center">
            <v-col cols="12" md="10" lg="8">
              <v-card class="db-preplan-card" outlined color="#F5F5F7">
                <v-card-title class="db-preplan-title" style="color: #444;">Pre-Plan</v-card-title>
                <v-progress-linear
                  v-if="loading"
                  indeterminate
                  color="grey"
                  height="4"
                  class="mb-2"
                />
                
                <v-card-text v-if="!loading && prePlan" class="db-preplan-text" style="color: #444;">
                  {{ prePlan }}
                </v-card-text>
                <v-card-actions v-if="!loading && prePlan">
                  <v-btn
                    to="/connections"
                    color="#EC0016"
                    variant="flat"
                    class="ml-auto"
                    @click="fetchConnections()"
                  >
                    Plane meinen Trip ->
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
            <div class="db-search-box">
              <v-text-field
                v-model="prompt.text"
                append-inner-icon="mdi-send"
                label="Verbindung suchen… Start, Ziel oder Bahnhof eingeben"
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
                  Manuelle Eingabe von Reisedaten
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
  import { ref, computed } from 'vue'
  import { useBackendCalls } from '@/stores/backendCalls'
  import DateTimePicker from '@/components/DateTimePicker.vue'

  const backendCallsStore = useBackendCalls()

  const verkehrsmittel = ref(['ICE', 'IC', 'RE', 'RB', 'S-Bahn', 'U-Bahn', 'Tram', 'Bus'])
  const umstiegszeiten = ref(['5 Minuten', '10 Minuten', '15 Minuten', '20 Minuten', '30 Minuten'])

  const showPrePlan = ref(false)
  const loading = ref(false)

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

  const prePlan = computed(() => backendCallsStore.prePlan)

  async function fetchConnections () {
    loading.value = true
    await backendCallsStore.fetchConnections()
    loading.value = false
  }

  async function send () {
    loading.value = true
    showPrePlan.value = true
    await backendCallsStore.fetchPrePlanForPrompt(prompt.value.text)
    loading.value = false
  }

</script>

<style scoped>
.db-page {
  min-height: 100vh;
  background: #F0F3F5 url('@/assets/ice_bild.png') no-repeat center top;
  background-size: 1700px auto;
  padding: 2rem 1rem;
}

@media (max-width: 768px) {
  .db-page {
    background-size: cover;
    background-position: center top;
  }
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

.db-preplan-card {
  margin-bottom: 2rem;
  background: #F5F5F7;
  border: none;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(44,44,44,0.07);
  padding: 1.5rem 2rem;
}
.db-preplan-title {
  color: #EC0016;
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}
.db-preplan-text {
  color: #282D37;
  font-size: 1.05rem;
  font-family: inherit;
  white-space: pre-line;
}
</style>
