import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { entityApi } from '../services/api.js'

export const useEntitiesStore = defineStore('entities', () => {
  // State
  const entities = ref([])
  const currentEntity = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const searchQuery = ref('')
  const pagination = ref({
    skip: 0,
    limit: 50,
    total: 0
  })

  // Getters
  const filteredEntities = computed(() => {
    if (!searchQuery.value) return entities.value
    const query = searchQuery.value.toLowerCase()
    return entities.value.filter(entity =>
      entity.name.toLowerCase().includes(query) ||
      entity.description.toLowerCase().includes(query)
    )
  })

  const sortedEntities = computed(() => {
    return [...filteredEntities.value].sort((a, b) => b.rating - a.rating)
  })

  const isLoading = computed(() => loading.value)

  // Actions
  const fetchEntities = async (params = {}) => {
    try {
      loading.value = true
      error.value = null

      const response = await entityApi.list(params)
      entities.value = response.data

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch entities'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const fetchEntity = async (id) => {
    try {
      loading.value = true
      error.value = null

      const response = await entityApi.get(id)
      currentEntity.value = response.data

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch entity'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const createEntity = async (entityData) => {
    try {
      loading.value = true
      error.value = null

      const response = await entityApi.create(entityData)
      entities.value.push(response.data)

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create entity'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const updateEntity = async (id, entityData) => {
    try {
      loading.value = true
      error.value = null

      const response = await entityApi.update(id, entityData)
      const index = entities.value.findIndex(e => e.id === id)
      if (index !== -1) {
        entities.value[index] = response.data
      }

      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update entity'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const deleteEntity = async (id) => {
    try {
      loading.value = true
      error.value = null

      await entityApi.delete(id)
      entities.value = entities.value.filter(e => e.id !== id)

      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete entity'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const setSearchQuery = (query) => {
    searchQuery.value = query
  }

  const clearError = () => {
    error.value = null
  }

  const refreshEntities = () => {
    return fetchEntities({ skip: pagination.value.skip, limit: pagination.value.limit })
  }

  return {
    // State
    entities,
    currentEntity,
    loading,
    error,
    searchQuery,
    pagination,

    // Getters
    filteredEntities,
    sortedEntities,
    isLoading,

    // Actions
    fetchEntities,
    fetchEntity,
    createEntity,
    updateEntity,
    deleteEntity,
    setSearchQuery,
    clearError,
    refreshEntities
  }
})