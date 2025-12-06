import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useBackendCalls = defineStore('BackendCalls', () => {
  const prePlan = ref(null)
  const connections = ref([])

  async function fetchPrePlanForPrompt(prompt) {
    console.log("send prePlan")
  }


  return {
    prePlan,
    connections,
    fetchPrePlanForPrompt
  }
})
