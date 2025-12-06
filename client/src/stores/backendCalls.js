import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useBackendCalls = defineStore('BackendCalls', () => {
  const prePlan = ref(null)
  const connections = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchPrePlanForPrompt(prompt) {
    console.log("send prePlan")
  }

  async function fetchConnections(origin, destination, date = null) {
    loading.value = true
    error.value = null
    try {
      const response = await fetch('/api/v1/connections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          origin,
          destination,
          date
        })
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
    fetchPrePlanForPrompt,
    fetchConnections
  }
})
