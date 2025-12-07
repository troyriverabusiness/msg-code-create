<template>
  <div>
    <!-- Seat Selection Dialog -->
    <v-dialog v-model="showSeatDialog" width="900" persistent>
      <v-card class="seat-dialog-card">
        <v-card-title class="seat-dialog-title">
          <div class="title-content">
            <span>{{ selectedCoach?.type }} {{ selectedCoach?.number }} - Sitzplatzwahl</span>
            <v-btn icon size="small" @click="showSeatDialog = false" class="ml-auto">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </div>
        </v-card-title>

        <v-divider />

        <v-card-text class="seat-selection-content">
          <!-- Seat Info -->
          <div class="seat-info-bar">
            <div class="info-item">
              <span class="info-dot available"></span>
              <span>Verfügbar</span>
            </div>
            <div class="info-item">
              <span class="info-dot reserved"></span>
              <span>Reserviert</span>
            </div>
            <div class="info-item">
              <span class="info-dot occupied"></span>
              <span>Besetzt</span>
            </div>
            <div class="info-item">
              <span class="info-dot disabled"></span>
              <span>Nicht verfügbar</span>
            </div>
          </div>

          <!-- Seat Map -->
          <div class="seat-map-container">
            <!-- Coach Front -->
            <div class="coach-front">VORNE</div>

            <!-- Seat Rows -->
            <div class="seat-rows">
              <div v-for="row in seatRows" :key="row" class="seat-row">
                <div class="row-number">{{ row }}</div>
                <div class="seats-group">
                  <!-- Left side (A, B) or Luggage Block -->
                  <div v-if="hasLuggage(row) && getLuggageSide(row) === 'left'" class="luggage-block">
                    <v-icon size="small" color="#999">mdi-briefcase</v-icon>
                  </div>
                  <div v-else class="seats-side">
                    <div
                      v-for="seat in getRowSeats(row, 'left')"
                      :key="seat.id"
                      class="seat"
                      :class="getSeatClass(seat)"
                      @click="selectSeat(seat)"
                      :title="`${seat.id} - ${seat.status}`"
                    >
                      <span class="seat-letter">{{ seat.letter }}</span>
                    </div>
                  </div>

                  <!-- Aisle -->
                  <div class="aisle"></div>

                  <!-- Right side (C, D) or Luggage Block -->
                  <div v-if="hasLuggage(row) && getLuggageSide(row) === 'right'" class="luggage-block">
                    <v-icon size="small" color="#999">mdi-briefcase</v-icon>
                  </div>
                  <div v-else class="seats-side">
                    <div
                      v-for="seat in getRowSeats(row, 'right')"
                      :key="seat.id"
                      class="seat"
                      :class="getSeatClass(seat)"
                      @click="selectSeat(seat)"
                      :title="`${seat.id} - ${seat.status}`"
                    >
                      <span class="seat-letter">{{ seat.letter }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Coach Back -->
            <div class="coach-back">HINTEN</div>
          </div>

          <!-- Selected Seats Display -->
          <div v-if="selectedSeats.length > 0" class="selected-seats-info">
            <strong>Ausgewählte Sitze:</strong>
            <div class="selected-seat-list">
              <v-chip
                v-for="seat in selectedSeats"
                :key="seat.id"
                closable
                @click:close="deselectSeat(seat)"
                color="#EC0016"
                text-color="white"
              >
                {{ seat.id }}
              </v-chip>
            </div>
          </div>
        </v-card-text>

        <v-divider />

        <v-card-actions class="seat-actions">
          <v-spacer />
          <v-btn variant="text" @click="showSeatDialog = false">
            Abbrechen
          </v-btn>
          <v-btn color="#EC0016" @click="confirmSeats" :disabled="selectedSeats.length === 0">
            Bestätigen ({{ selectedSeats.length }})
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const showSeatDialog = ref(false)
const selectedCoach = ref(null)
const selectedSeats = ref([])

// Generate random luggage rows for this coach session
const luggageRows = ref(generateRandomLuggageRows())
const luggageSides = ref(generateRandomLuggageSides())

// Define seat rows
const seatRows = ref([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

// Define all seats with status
const allSeats = ref([
  // Row 1
  { id: '1A', row: 1, letter: 'A', side: 'left', status: 'available' },
  { id: '1B', row: 1, letter: 'B', side: 'left', status: 'available' },
  { id: '1C', row: 1, letter: 'C', side: 'right', status: 'occupied' },
  { id: '1D', row: 1, letter: 'D', side: 'right', status: 'available' },
  // Row 2
  { id: '2A', row: 2, letter: 'A', side: 'left', status: 'available' },
  { id: '2B', row: 2, letter: 'B', side: 'left', status: 'available' },
  { id: '2C', row: 2, letter: 'C', side: 'right', status: 'reserved' },
  { id: '2D', row: 2, letter: 'D', side: 'right', status: 'reserved' },
  // Row 3
  { id: '3A', row: 3, letter: 'A', side: 'left', status: 'occupied' },
  { id: '3B', row: 3, letter: 'B', side: 'left', status: 'available' },
  { id: '3C', row: 3, letter: 'C', side: 'right', status: 'available' },
  { id: '3D', row: 3, letter: 'D', side: 'right', status: 'occupied' },
  // Row 4-10 (simplified)
  ...generateSeats(4, 10)
])

function generateSeats(startRow, endRow) {
  const seats = []
  for (let row = startRow; row <= endRow; row++) {
    const letters = ['A', 'B', 'C', 'D']
    const sides = { A: 'left', B: 'left', C: 'right', D: 'right' }
    const statuses = ['available', 'available', 'available', 'available']
    
    letters.forEach((letter, index) => {
      seats.push({
        id: `${row}${letter}`,
        row,
        letter,
        side: sides[letter],
        status: statuses[Math.floor(Math.random() * 3)] || 'available'
      })
    })
  }
  return seats
}

function getRowSeats(row, side) {
  const letters = side === 'left' ? ['A', 'B'] : ['C', 'D']
  return allSeats.value.filter(s => s.row === row && letters.includes(s.letter))
}

function generateRandomLuggageRows() {
  // Generate 2-3 random rows out of 10 that will have luggage compartments
  // With one near the front (rows 1-3) and one near the back (rows 8-10)
  const luggageRowsSet = new Set()
  
  // Always add one near the front
  luggageRowsSet.add(Math.floor(Math.random() * 3) + 1) // rows 1-3
  
  // Always add one near the back
  luggageRowsSet.add(Math.floor(Math.random() * 3) + 8) // rows 8-10
  
  // Randomly add one more in the middle
  if (Math.random() > 0.4) {
    luggageRowsSet.add(Math.floor(Math.random() * 4) + 4) // rows 4-7
  }
  
  return Array.from(luggageRowsSet).sort((a, b) => a - b)
}

function hasLuggage(row) {
  return luggageRows.value.includes(row)
}

function generateRandomLuggageSides() {
  // For each luggage row, randomly decide if it's left (A,B) or right (C,D)
  // Make sure not all are on the same side
  const sides = {}
  const rows = luggageRows.value
  let leftCount = 0
  let rightCount = 0
  
  rows.forEach((row, index) => {
    let side
    // Ensure they're not all on one side
    if (index < Math.ceil(rows.length / 2)) {
      side = 'left'
      leftCount++
    } else {
      side = 'right'
      rightCount++
    }
    // Add some randomness while maintaining balance
    if (Math.random() > 0.6 && leftCount !== rightCount) {
      side = side === 'left' ? 'right' : 'left'
    }
    sides[row] = side
  })
  return sides
}

function getLuggageSide(row) {
  return luggageSides.value[row] || 'right'
}

function getSeatClass(seat) {
  return {
    [`status-${seat.status}`]: true,
    'seat-selected': selectedSeats.value.some(s => s.id === seat.id)
  }
}

function selectSeat(seat) {
  if (seat.status === 'available') {
    if (selectedSeats.value.some(s => s.id === seat.id)) {
      deselectSeat(seat)
    } else {
      selectedSeats.value.push(seat)
    }
  }
}

function deselectSeat(seat) {
  selectedSeats.value = selectedSeats.value.filter(s => s.id !== seat.id)
}

function confirmSeats() {
  console.log('Selected seats:', selectedSeats.value)
  showSeatDialog.value = false
}

function openCoachSeats(coach) {
  selectedCoach.value = coach
  selectedSeats.value = []
  // Generate new random luggage configuration for each coach
  luggageRows.value = generateRandomLuggageRows()
  luggageSides.value = generateRandomLuggageSides()
  showSeatDialog.value = true
}

// Export for use in parent component
defineExpose({
  openCoachSeats,
  showSeatDialog
})
</script>

<style scoped>
.seat-dialog-card {
  background: white;
}

.seat-dialog-title {
  padding: 1.5rem;
  font-weight: 700;
  font-size: 1.2rem;
  color: #282D37;
}

.title-content {
  display: flex;
  align-items: center;
  width: 100%;
}

.seat-selection-content {
  padding: 2rem;
  max-height: 600px;
  overflow-y: auto;
}

.seat-info-bar {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #282D37;
}

.info-dot {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  flex-shrink: 0;
}

.info-dot.available {
  background: #33b504;
  border: 2px solid #2a9603;
}

.info-dot.reserved {
  background: #faab23;
  border: 2px solid #e69700;
}

.info-dot.occupied {
  background: #d93128;
  border: 2px solid #b50000;
}

.info-dot.disabled {
  background: #ccc;
  border: 2px solid #999;
}

.seat-map-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  margin: 2rem 0;
}

.coach-front,
.coach-back {
  background: #003366;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 700;
  font-size: 0.9rem;
  letter-spacing: 1px;
}

.seat-rows {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-left: -2.8rem;
}

.seat-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.row-number {
  min-width: 2rem;
  text-align: center;
  font-weight: 700;
  color: #282D37;
}

.seats-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.seats-side {
  display: flex;
  gap: 0.5rem;
}

.aisle {
  width: 1.5rem;
  height: auto;
}

.seat {
  width: 32px;
  height: 32px;
  border: 2px solid #ccc;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: not-allowed;
  font-size: 0.75rem;
  font-weight: 700;
  background: #f0f0f0;
  transition: all 0.2s ease;
  position: relative;
}

.seat-letter {
  position: absolute;
  top: 2px;
  font-size: 0.6rem;
  color: white;
  font-weight: 900;
}

.seat.status-available {
  background: #33b504;
  border-color: #2a9603;
  color: white;
  cursor: pointer;
}

.seat.status-available:hover {
  transform: scale(1.1);
  box-shadow: 0 0 8px rgba(51, 181, 4, 0.4);
}

.seat.status-reserved {
  background: #faab23;
  border-color: #e69700;
  color: white;
  cursor: not-allowed;
}

.seat.status-occupied {
  background: #d93128;
  border-color: #b50000;
  color: white;
  cursor: not-allowed;
}

.seat.status-disabled {
  background: #e8e8e8;
  border-color: #999;
  color: #999;
  cursor: not-allowed;
}

.seat.seat-selected {
  box-shadow: 0 0 12px rgba(236, 0, 22, 0.6);
  transform: scale(1.15);
  border-color: #EC0016;
}

.selected-seats-info {
  margin-top: 2rem;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
  border-left: 4px solid #EC0016;
}

.selected-seat-list {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

.seat-actions {
  padding: 1rem 1.5rem;
}

.luggage-block {
  width: 69px;
  height: 32px;
  background: #e8e8e8;
  border: 2px dashed #999;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: help;
  flex-shrink: 0;
}
</style>
