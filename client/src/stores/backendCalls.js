import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useBackendCalls = defineStore('BackendCalls', () => {
  const prePlan = ref(null)
  //TODO CHANGE THIS WHEN API IS READY
  const connections = ref([
    {
      id: "j_direct_001",
      startStation: {
        name: "Berlin Hbf",
        eva: "8011160"
      },
      endStation: {
        name: "Hamburg Hbf",
        eva: "8002549"
      },
      transfers: 0,
      totalTime: 105,
      description: "Direct Connection",
      legs: [
        {
          origin: {
            name: "Berlin Hbf",
            eva: "8011160"
          },
          destination: {
            name: "Hamburg Hbf",
            eva: "8002549"
          },
          train: {
            name: "ICE 802",
            trainNumber: "802",
            startLocation: {
              name: "München Hbf",
              eva: "8000261"
            },
            endLocation: {
              name: "Hamburg-Altona",
              eva: "8002553"
            },
            departureTime: "08:00:00",
            arrivalTime: "09:45:00",
            path: [],
            platform: 13,
            wagons: [
              1,
              2,
              3,
              4
            ]
          },
          departureTime: "08:00:00",
          arrivalTime: "09:45:00"
        },
        {
          origin: {
            name: "C Hbf",
            eva: "8011160"
          },
          destination: {
            name: "B Hbf",
            eva: "8002549"
          },
          train: {
            name: "ICE 84",
            trainNumber: "82",
            startLocation: {
              name: "München Hbf",
              eva: "8000261"
            },
            endLocation: {
              name: "Hamburg-Altona",
              eva: "8002553"
            },
            departureTime: "08:00:00",
            arrivalTime: "09:45:00",
            path: [],
            platform: 4,
            wagons: [
              1,
              2,
              3
            ]
          },
          departureTime: "10:00:00",
          arrivalTime: "11:45:00"
        },
        {
          origin: {
            name: "Berlin Hbf",
            eva: "8011160"
          },
          destination: {
            name: "Hamburg Hbf",
            eva: "8002549"
          },
          train: {
            name: "ICE 802",
            trainNumber: "802",
            startLocation: {
              name: "München Hbf",
              eva: "8000261"
            },
            endLocation: {
              name: "Hamburg-Altona",
              eva: "8002553"
            },
            departureTime: "08:00:00",
            arrivalTime: "09:45:00",
            path: [],
            platform: 13,
            wagons: [
              1,
              2,
              3,
              4
            ]
          },
          departureTime: "08:00:00",
          arrivalTime: "09:45:00"
        }
      ]   
    },
    {
      id: "j_transfer_002",
      startStation: {
        name: "Frankfurt (Main) Hbf",
        eva: "8000105"
      },
      endStation: {
        name: "München Hbf",
        eva: "8000261"
      },
      transfers: 1,
      totalTime: 240,
      description: "1 Transfer",
      legs: [
        {
          origin: {
            name: "Frankfurt (Main) Hbf",
            eva: "8000105"
          },
          destination: {
            name: "Mannheim Hbf",
            eva: "8000244"
          },
          train: {
            name: "ICE 105",
            trainNumber: "105",
            startLocation: {
              name: "Amsterdam Centraal",
              eva: "8400058"
            },
            endLocation: {
              name: "Basel SBB",
              eva: "8500010"
            },
            departureTime: "10:00:00",
            arrivalTime: "10:45:00",
            path: [],
            platform: 7,
            wagons: []
          },
          departureTime: "10:00:00",
          arrivalTime: "10:45:00"
        },
        {
          origin: {
            name: "Mannheim Hbf",
            eva: "8000244"
          },
          destination: {
            name: "München Hbf",
            eva: "8000261"
          },
          train: {
            name: "ICE 513",
            trainNumber: "513",
            startLocation: {
              name: "Dortmund Hbf",
              eva: "8000080"
            },
            endLocation: {
              name: "München Hbf",
              eva: "8000261"
            },
            departureTime: "11:00:00",
            arrivalTime: "14:00:00",
            path: [],
            platform: 4,
            wagons: []
          },
          departureTime: "11:00:00",
          arrivalTime: "14:00:00"
        }
      ]
    }
  ]
)

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

  async function fetchConnections(reiseplan) {
    console.log("Fetching connections for reiseplan:", reiseplan);
    try {
      const response = await axios.post('http://localhost:8000/api/v1/connections', { reiseplan }, {
        headers: {
          'Content-Type': 'application/json',
        }
      })
      console.log("Connections response:", response.data);
      
      connections.value = response.data
      return response.data
    } catch (error) {
      console.error('Error fetching connections:', error.response?.data?.detail || error.message)
      return null
    }
  }


  return {
    prePlan,
    connections,
    fetchPrePlanForPrompt,
    fetchConnections
  }
})
