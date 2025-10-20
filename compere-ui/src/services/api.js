import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('compere_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token on unauthorized
      localStorage.removeItem('compere_token')
      // Optionally redirect to login
    }
    return Promise.reject(error)
  }
)

// Entity API
export const entityApi = {
  // List entities with optional search and pagination
  list: (params = {}) => api.get('/entities/', { params }),

  // Get single entity
  get: (id) => api.get(`/entities/${id}`),

  // Create new entity
  create: (data) => api.post('/entities/', data),

  // Update entity
  update: (id, data) => api.put(`/entities/${id}`, data),

  // Delete entity
  delete: (id) => api.delete(`/entities/${id}`)
}

// Comparison API
export const comparisonApi = {
  // List comparisons
  list: (params = {}) => api.get('/comparisons/', { params }),

  // Get single comparison
  get: (id) => api.get(`/comparisons/${id}`),

  // Create new comparison
  create: (data) => api.post('/comparisons/', data),

  // Get next comparison suggestion
  getNext: () => api.get('/comparisons/next')
}

// Rating API
export const ratingApi = {
  // Get ratings leaderboard
  getRatings: () => api.get('/ratings'),

  // Get similar/dissimilar entities
  getSimilarEntities: () => api.get('/similar_entities'),
  getDissimilarEntities: () => api.get('/dissimilar_entities')
}

// MAB API
export const mabApi = {
  // Get next comparison from MAB algorithm
  getNextComparison: () => api.get('/mab/next_comparison'),

  // Update MAB state
  update: (comparisonId) => api.post(`/mab/update`, null, {
    params: { comparison_id: comparisonId }
  })
}

// Auth API
export const authApi = {
  // Login
  login: (username, password) => api.post('/auth/token', null, {
    params: { username, password }
  }),

  // Get current user
  getCurrentUser: () => api.get('/auth/users/me')
}

// Health check
export const healthApi = {
  check: () => api.get('/docs')
}

export default api