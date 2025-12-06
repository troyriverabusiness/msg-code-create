import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useBackendCalls = defineStore('BackendCalls', () => {
  const prePlan = ref(null)
  const connections = ref([])

  async function fetchPrePlanForPrompt(prompt) {
    console.log("Fetching prePlan for prompt:", prompt);
    try {
      const response = await axios.post('http://localhost:8000/api/v1/chat', { message: prompt }, {
        headers: {
          'Content-Type': 'application/json',
        }
      })
      console.log("AAA", response.data);
      
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
    fetchPrePlanForPrompt
  }
})
