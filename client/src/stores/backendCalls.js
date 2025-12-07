import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const SESSION_STORAGE_KEY = 'chat_session_id'

export const useBackendCalls = defineStore('BackendCalls', () => {
  const prePlan = ref(null)
  const connections = ref([])
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
    console.log("Fetching prePlan for prompt:", prompt);
    try {
      const headers = { 'Content-Type': 'application/json' }
      
      if (sessionId.value) {
        headers['X-Session-Id'] = sessionId.value
      }

      const response = await axios.post('http://localhost:8000/api/v1/chat', { message: prompt }, {
        headers
      })
      console.log("AAA", response.data);
      
      if (response.data.session_id) {
        setSessionId(response.data.session_id)
      }

      prePlan.value = response.data.message
      return response.data
    } catch (error) {
      prePlan.value = 'Error fetching prePlan: ' + (error.response?.data?.detail || error.message)
      return null
    }
  }


  return {
    prePlan,
    connections,
    sessionId,
    fetchPrePlanForPrompt
  }
})
