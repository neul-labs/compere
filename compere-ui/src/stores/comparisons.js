import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { comparisonApi, ratingApi, mabApi } from '../services/api.js'

export const useComparisonsStore = defineStore('comparisons', () => {
  // State
  const comparisons = ref([])
  const currentComparison = ref(null)
  const nextComparison = ref(null)
  const mabSuggestion = ref(null)
  const ratings = ref([])
  const loading = ref(false)
  const error = ref(null)
  const stats = ref({
    totalComparisons: 0,
    recentComparisons: 0,
    averageRating: 1500
  })

  // Getters
  const isLoading = computed(() => loading.value)
  const hasNextComparison = computed(() => !!nextComparison.value)
  const hasMabSuggestion = computed(() => !!mabSuggestion.value)

  const comparisonHistory = computed(() => {
    return [...comparisons.value].sort((a, b) =>
      new Date(b.created_at) - new Date(a.created_at)
    )
  })

  const topRatedEntities = computed(() => {
    return [...ratings.value].sort((a, b) => b.rating - a.rating).slice(0, 10)
  })

  // Actions
  const fetchComparisons = async (params = {}) => {
    try {
      loading.value = true
      error.value = null

      const response = await comparisonApi.list(params)
      comparisons.value = response.data
      stats.value.totalComparisons = response.data.length

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch comparisons'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const fetchRatings = async () => {
    try {
      const response = await ratingApi.getRatings()
      ratings.value = response.data

      if (response.data.length > 0) {
        const totalRating = response.data.reduce((sum, entity) => sum + entity.rating, 0)
        stats.value.averageRating = Math.round(totalRating / response.data.length)
      }

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch ratings'
      return { success: false, error: error.value }
    }
  }

  const getNextComparison = async () => {
    try {
      loading.value = true
      error.value = null

      const response = await comparisonApi.getNext()
      nextComparison.value = response.data

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to get next comparison'
      nextComparison.value = null
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const getMabSuggestion = async () => {
    try {
      const response = await mabApi.getNextComparison()
      mabSuggestion.value = response.data

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to get MAB suggestion'
      mabSuggestion.value = null
      return { success: false, error: error.value }
    }
  }

  const createComparison = async (comparisonData) => {
    try {
      loading.value = true
      error.value = null

      const response = await comparisonApi.create(comparisonData)
      comparisons.value.unshift(response.data)
      stats.value.totalComparisons++

      // Update MAB after comparison
      await mabApi.update(response.data.id)

      // Refresh ratings after comparison
      await fetchRatings()

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create comparison'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const submitComparison = async (entity1Id, entity2Id, winnerId) => {
    const comparisonData = {
      entity1_id: entity1Id,
      entity2_id: entity2Id,
      selected_entity_id: winnerId
    }

    const result = await createComparison(comparisonData)

    if (result.success) {
      // Clear current comparison and get next one
      nextComparison.value = null
      await getNextComparison()
      await getMabSuggestion()
    }

    return result
  }

  const clearError = () => {
    error.value = null
  }

  const refreshData = async () => {
    await Promise.all([
      fetchComparisons(),
      fetchRatings(),
      getMabSuggestion()
    ])
  }

  return {
    // State
    comparisons,
    currentComparison,
    nextComparison,
    mabSuggestion,
    ratings,
    loading,
    error,
    stats,

    // Getters
    isLoading,
    hasNextComparison,
    hasMabSuggestion,
    comparisonHistory,
    topRatedEntities,

    // Actions
    fetchComparisons,
    fetchRatings,
    getNextComparison,
    getMabSuggestion,
    createComparison,
    submitComparison,
    clearError,
    refreshData
  }
})