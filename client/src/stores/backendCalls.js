import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const SESSION_STORAGE_KEY = 'chat_session_id'

export const useBackendCalls = defineStore('BackendCalls', () => {
  const prePlan = ref(null)
  const prePlanParams = ref(null)
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
      prePlanParams.value = response.data.search_params
      return response.data
    } catch (error) {
      const errorDetail = error.response?.data?.detail || error.message || 'Unbekannter Fehler'
      prePlan.value = 'Error fetching prePlan: ' + errorDetail
      return null
    }
  }

  async function searchStations(query) {
    if (!query || query.length < 2) return []
    try {
      const response = await fetch(`/api/v1/stations?q=${encodeURIComponent(query)}`)
      if (!response.ok) throw new Error('Failed to fetch stations')
      const data = await response.json()
      return data.stations || []
    } catch (e) {
      console.error("Station search failed:", e)
      return []
    }
  }

  async function fetchConnections(origin, destination, date, via = null, minTransferTime = 0) {
    loading.value = true
    error.value = null
    connections.value = []

    try {
      const params = {
        start: origin,
        end: destination,
        departure_time: date
      }
      if (via) {
        params.via = via
        if (minTransferTime > 0) {
          params.min_transfer_time = minTransferTime
        }
      }

      // Use axios for consistency with other calls (though searchStations uses fetch)
      // Note: axios params serialization handles simple objects well.
      const response = await axios.get('/api/v1/connections', { params })

      connections.value = response.data.journeys || []
    } catch (e) {
      console.error("Failed to fetch connections:", e)
      error.value = e.response?.data?.detail || e.message || "Failed to fetch connections"
      connections.value = []
    } finally {
      loading.value = false
    }
  }

  return {
    prePlan,
    prePlanParams,
    connections,
    loading,
    error,
    sessionId,
    fetchPrePlanForPrompt,
    fetchConnections,
    searchStations,
    setSessionId // Expose setSessionId if needed by other components, though typically not directly.
  }
})
