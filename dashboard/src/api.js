import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || ''

export const api = {
  overview: () => axios.get(`${BASE}/analytics/overview`).then(r => r.data),
  intents: (days = 7) => axios.get(`${BASE}/analytics/intents?days=${days}`).then(r => r.data),
  sentiment: (hours = 24) => axios.get(`${BASE}/analytics/sentiment?hours=${hours}`).then(r => r.data),
  recentCalls: (limit = 20) => axios.get(`${BASE}/analytics/calls?limit=${limit}`).then(r => r.data),
  auth: (days = 7) => axios.get(`${BASE}/analytics/auth?days=${days}`).then(r => r.data),
}
