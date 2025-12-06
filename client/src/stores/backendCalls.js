import { defineStore } from 'pinia'

export const useBackendCalls = defineStore('BackendCalls', {
  state: () => ({
    connections: [],
  }),
  actions: {
    send(prompt) {
      console.log(prompt)
    },
  },
})
