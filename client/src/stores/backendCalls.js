import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useBackendCalls = defineStore('BackendCalls', () => {
  const prePlan = ref(null)
  const sessionId = ref(null)
  //TODO CHANGE THIS WHEN API IS READY
  const connections = ref(
   [
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
            path: [
              {
                station: {
                  name: "Berlin-Spandau",
                  eva: "8010404"
                },
                arrivalTime: "08:15:00",
                departureTime: "08:17:00"
              },
              {
                station: {
                  name: "Wittenberge",
                  eva: "8010382"
                },
                arrivalTime: "08:50:00",
                departureTime: "08:52:00"
              },
              {
                station: {
                  name: "Ludwigslust",
                  eva: "8010217"
                },
                arrivalTime: "09:10:00",
                departureTime: "09:12:00"
              },
              {
                station: {
                  name: "Büchen",
                  eva: "8010069"
                },
                arrivalTime: "09:30:00",
                departureTime: "09:32:00"
              }
            ],
            platform: 13,
            wagons: [
              1,
              2,
              3
            ]
          },
          departureTime: "08:00:00",
          arrivalTime: "09:45:00",
          delayInMinutes: 0
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
            path: [
              {
                station: {
                  name: "Frankfurt(M) Flughafen Fernbf",
                  eva: "8000105"
                },
                arrivalTime: "10:15:00",
                departureTime: "10:17:00"
              }
            ],
            platform: 7,
            wagons: []
          },
          departureTime: "10:00:00",
          arrivalTime: "10:45:00",
          delayInMinutes: 5
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
            path: [
              {
                station: {
                  name: "Stuttgart Hbf",
                  eva: "8000096"
                },
                arrivalTime: "11:40:00",
                departureTime: "11:45:00"
              },
              {
                station: {
                  name: "Ulm Hbf",
                  eva: "8000170"
                },
                arrivalTime: "12:30:00",
                departureTime: "12:32:00"
              },
              {
                station: {
                  name: "Augsburg Hbf",
                  eva: "8000013"
                },
                arrivalTime: "13:15:00",
                departureTime: "13:17:00"
              }
            ],
            platform: 4,
            wagons: []
          },
          departureTime: "11:00:00",
          arrivalTime: "14:00:00",
          delayInMinutes: 0
        }
      ]
    }
  ]
)

  async function fetchPrePlanForPrompt(prompt) {
    try {
      const response = await axios.post('http://localhost:8000/api/v1/chat', { message: prompt, sessionId: sessionId.value }, {
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if(sessionId.value === null) {
        sessionId.value = response.data.session_id
      }
      prePlan.value = response.data.message
      return response.data
    } catch (error) {
      prePlan.value = 'Error fetching prePlan: ' + (error.response?.data?.detail || error.message)
      return null
    }
  }

  async function fetchConnections(reiseplan) {
    try {
      const response = await axios.post('http://localhost:8000/api/v1/connections', { reiseplan }, {
        headers: {
          'Content-Type': 'application/json',
        }
      })

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
