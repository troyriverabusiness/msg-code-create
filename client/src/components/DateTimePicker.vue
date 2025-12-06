<template>
  <v-menu v-model="dateMenu" :close-on-content-click="false" transition="scale-transition">
    <template #activator="{ props }">
      <v-text-field
        :model-value="displayValue"
        :label="label"
        prepend-inner-icon="mdi-calendar-clock"
        readonly
        clearable
        v-bind="props"
        @click:clear="clearDateTime"
      />
    </template>
    <v-date-picker
      v-if="!showTimePicker"
      v-model="selectedDate"
      :show-current="true"
      color="primary"
    >
      <template #actions>
        <v-btn text @click="dateMenu = false">Cancel</v-btn>
        <v-btn text color="primary" @click="onDateSelected">Next</v-btn>
      </template>
    </v-date-picker>
    <v-time-picker
      v-else
      v-model="selectedTime"
      format="24hr"
      color="primary"
    >
      <template #actions>
        <v-btn text @click="showTimePicker = false">Back</v-btn>
        <v-btn text color="primary" @click="onTimeSelected">OK</v-btn>
      </template>
    </v-time-picker>
  </v-menu>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { format, parse } from 'date-fns'

const props = defineProps({
  modelValue: {
    type: String,
    default: null
  },
  label: {
    type: String,
    default: 'Datum & Uhrzeit'
  }
})

const emit = defineEmits(['update:modelValue'])

const dateMenu = ref(false)
const showTimePicker = ref(false)
const selectedDate = ref(null)
const selectedTime = ref('12:00')

const displayValue = computed(() => {
  if (!props.modelValue) return ''
  try {
    const date = parse(props.modelValue, 'yyyy-MM-dd HH:mm', new Date())
    return format(date, 'dd.MM.yyyy HH:mm')
  } catch {
    return props.modelValue
  }
})

// Parse initial value if provided
watch(() => props.modelValue, (val) => {
  if (val) {
    try {
      const date = parse(val, 'yyyy-MM-dd HH:mm', new Date())
      selectedDate.value = date
      const timeParts = val.split(' ')
      if (timeParts.length >= 2) selectedTime.value = timeParts[1]
    } catch {
      // fallback
    }
  }
}, { immediate: true })

function onDateSelected() {
  showTimePicker.value = true
}

function onTimeSelected() {
  // selectedDate is a Date object from v-date-picker
  const formattedDate = format(selectedDate.value, 'yyyy-MM-dd')
  const dateTimeString = `${formattedDate} ${selectedTime.value}`
  emit('update:modelValue', dateTimeString)
  showTimePicker.value = false
  dateMenu.value = false
}

function clearDateTime() {
  selectedDate.value = null
  selectedTime.value = '12:00'
  emit('update:modelValue', null)
}

// Reset time picker state when menu closes
watch(dateMenu, (open) => {
  if (!open) {
    showTimePicker.value = false
  }
})
</script>
