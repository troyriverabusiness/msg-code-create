<template>
  <v-card class="bingo-card pa-4 mt-4" elevation="2">
    <div class="d-flex align-center justify-space-between mb-4">
      <h3 class="text-h6 font-weight-bold d-flex align-center">
        <v-icon color="primary" class="mr-2">mdi-grid</v-icon>
        DB Delay Bingo
      </h3>
      <v-btn
        size="small"
        variant="text"
        color="grey"
        prepend-icon="mdi-refresh"
        @click="resetBingo"
      >
        Reset
      </v-btn>
    </div>

    <v-row dense>
      <v-col
        v-for="(phrase, index) in phrases"
        :key="index"
        cols="6"
        sm="4"
        md="3"
      >
        <v-card
          :class="['bingo-cell', { 'bingo-cell-active': isCollected(phrase) }]"
          variant="outlined"
          @click="togglePhrase(phrase)"
          v-ripple
        >
          <div class="bingo-content">
            <v-icon 
              v-if="isCollected(phrase)" 
              color="success" 
              class="bingo-check"
              size="small"
            >
              mdi-check-circle
            </v-icon>
            <span class="text-caption font-weight-medium">{{ phrase }}</span>
          </div>
        </v-card>
      </v-col>
    </v-row>
    
    <v-expand-transition>
      <div v-if="isBingo" class="bingo-win mt-4 pa-3 text-center rounded bg-success-lighten-4">
        <span class="text-h5">🎉 BINGO! 🎉</span>
        <div class="text-body-2 mt-1">You are a true DB veteran!</div>
      </div>
    </v-expand-transition>
  </v-card>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const STORAGE_KEY = 'db-bingo-collection'

const phrases = [
  "Verzögerung im Betriebsablauf",
  "Signalstörung",
  "Wagenreihung geändert",
  "Polizeieinsatz",
  "Schnee auf den Gleisen",
  "Warten auf Anschlussreisende",
  "Reparatur am Zug",
  "Weichenstörung",
  "Laut Fahrplanleitung gibt es diesen Zug nicht",
  "Personen im Gleis",
  "Technische Störung am Zug",
  "Verspätung aus vorheriger Fahrt"
]

const collected = ref(new Set())

onMounted(() => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      collected.value = new Set(parsed)
    } catch (e) {
      console.error('Failed to load bingo state', e)
    }
  }
})

function isCollected(phrase) {
  return collected.value.has(phrase)
}

function togglePhrase(phrase) {
  if (collected.value.has(phrase)) {
    collected.value.delete(phrase)
  } else {
    collected.value.add(phrase)
  }
  saveState()
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...collected.value]))
}

function resetBingo() {
  collected.value.clear()
  saveState()
}

const isBingo = computed(() => {
  // Simple bingo logic: at least 4 items collected
  // In a real grid we'd check rows/cols, but for this responsive layout
  // a simple count threshold is more robust
  return collected.value.size >= 4
})
</script>

<style scoped>
.bingo-card {
  background: linear-gradient(to bottom right, #ffffff, #f8f9fa);
}

.bingo-cell {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  border-color: #e0e0e0;
}

.bingo-cell:hover {
  background-color: #f5f5f5;
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.bingo-cell-active {
  background-color: #e8f5e9 !important;
  border-color: #4caf50 !important;
  color: #2e7d32;
}

.bingo-content {
  position: relative;
  z-index: 1;
  line-height: 1.2;
}

.bingo-check {
  position: absolute;
  top: 4px;
  right: 4px;
  opacity: 0.8;
}

.bingo-win {
  animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 2px solid #4caf50;
}

@keyframes popIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
