import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../services/api.js'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref(localStorage.getItem('compere_token'))
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isLoading = computed(() => loading.value)

  // Actions
  const login = async (username, password) => {
    try {
      loading.value = true
      error.value = null

      const response = await authApi.login(username, password)
      const { access_token } = response.data

      token.value = access_token
      localStorage.setItem('compere_token', access_token)

      // Get user info
      await getCurrentUser()

      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    error.value = null
    localStorage.removeItem('compere_token')
  }

  const getCurrentUser = async () => {
    if (!token.value) return

    try {
      loading.value = true
      const response = await authApi.getCurrentUser()
      user.value = response.data
    } catch (err) {
      // Token might be invalid
      logout()
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  // Initialize user if token exists
  if (token.value) {
    getCurrentUser()
  }

  return {
    // State
    token,
    user,
    loading,
    error,

    // Getters
    isAuthenticated,
    isLoading,

    // Actions
    login,
    logout,
    getCurrentUser,
    clearError
  }
})