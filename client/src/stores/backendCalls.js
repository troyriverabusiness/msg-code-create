import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const SESSION_STORAGE_KEY = 'chat_session_id'

export const useBackendCalls = defineStore('BackendCalls', () => {
  const prePlan = ref(null)
  const connections = ref([])
  const loading = ref(false)
  const error = ref(null)
  const sessionId = ref(localStorage.getItem(SESSION_STORAGE_KEY) || null)

  function setSessionId(id) {
    sessionId.value = id
    if (id) {
      localStorage.setItem(SESSION_STORAGE_KEY, id)
    } else {
      localStorage.removeItem(SESSION_STORAGE_KEY)
    }
  }

  async function fetchPrePlanForPrompt(prompt) {
    try {
      const headers = { 'Content-Type': 'application/json' }
      
      if (sessionId.value) {
        headers['X-Session-Id'] = sessionId.value
      }

      const response = await axios.post('/api/v1/chat', { message: prompt }, {
        headers
      })
      console.log("AAA", response.data);
      
      if (response.data.session_id) {
        setSessionId(response.data.session_id)
      }

      prePlan.value = response.data.message
      return response.data
    } catch (e) {
      prePlan.value = 'Error fetching prePlan: ' + (e.response?.data?.detail || e.message)
      return null
    }
  }

  async function fetchConnections(origin, destination, date = null) {
    loading.value = true
    error.value = null
    try {
      // Map frontend 'origin'/'destination' to backend 'start'/'end'
      const requestBody = {
        start: origin,
        end: destination,
        trip_plan: "", // Optional context
        departure_time: date
      }

      const response = await fetch('/api/v1/connections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      connections.value = data.journeys || []
    } catch (e) {
      console.error("Failed to fetch connections:", e)
      error.value = e.message
      connections.value = []
    } finally {
      loading.value = false
    }
  }

  return {
    prePlan,
    connections,
    loading,
    error,
    sessionId,
    fetchPrePlanForPrompt,
    fetchConnections,
    setSessionId // Expose setSessionId if needed by other components, though typically not directly.
  }
})
