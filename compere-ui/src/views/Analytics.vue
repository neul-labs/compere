<template>
  <div class="space-y-8">
    <div class="text-center">
      <h1 class="text-2xl font-bold text-surface-900 mb-4">Analytics & History</h1>
      <p class="text-surface-600 text-lg">Comparison history and system insights</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
      <!-- Recent Comparisons -->
      <div class="card p-6">
        <h2 class="text-lg font-bold text-surface-900 mb-6">Recent Comparisons</h2>
        <div class="space-y-4">
          <div
            v-for="comparison in recentComparisons.slice(0, 10)"
            :key="comparison.id"
            class="flex items-center space-x-4 p-3 rounded-lg bg-surface-100"
          >
            <div class="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white text-sm">
              {{ comparison.id }}
            </div>
            <div class="flex-1">
              <p class="font-medium text-surface-900">Comparison #{{ comparison.id }}</p>
              <p class="text-sm text-surface-500">
                {{ formatRelativeTime(comparison.created_at) }}
              </p>
            </div>
          </div>
        </div>

        <div v-if="recentComparisons.length === 0" class="text-center py-8">
          <i class="fas fa-chart-bar text-4xl text-surface-400 mb-2"></i>
          <p class="text-surface-500">No comparisons yet</p>
        </div>
      </div>

      <!-- System Stats -->
      <div class="card p-6">
        <h2 class="text-lg font-bold text-surface-900 mb-6">System Statistics</h2>
        <div class="space-y-6">
          <div class="grid grid-cols-2 gap-4">
            <div class="text-center p-4 rounded-lg bg-surface-100">
              <p class="text-3xl font-bold text-primary-600">{{ entitiesStore.entities.length }}</p>
              <p class="text-sm text-surface-500">Total Entities</p>
            </div>
            <div class="text-center p-4 rounded-lg bg-surface-100">
              <p class="text-3xl font-bold text-green-600">{{ comparisonsStore.comparisons.length }}</p>
              <p class="text-sm text-surface-500">Comparisons</p>
            </div>
          </div>

          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-surface-700">Average Rating</span>
              <span class="font-bold text-surface-900">{{ averageRating }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-surface-700">Highest Rating</span>
              <span class="font-bold text-green-600">{{ highestRating }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-surface-700">Lowest Rating</span>
              <span class="font-bold text-red-600">{{ lowestRating }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useEntitiesStore } from '../stores/entities.js'
import { useComparisonsStore } from '../stores/comparisons.js'
import { formatRating } from '../utils/simulation.js'

const entitiesStore = useEntitiesStore()
const comparisonsStore = useComparisonsStore()

const recentComparisons = computed(() => comparisonsStore.comparisonHistory)

const averageRating = computed(() => {
  if (entitiesStore.entities.length === 0) return 0
  const total = entitiesStore.entities.reduce((sum, e) => sum + e.rating, 0)
  return formatRating(total / entitiesStore.entities.length)
})

const highestRating = computed(() => {
  if (entitiesStore.entities.length === 0) return 0
  return formatRating(Math.max(...entitiesStore.entities.map(e => e.rating)))
})

const lowestRating = computed(() => {
  if (entitiesStore.entities.length === 0) return 0
  return formatRating(Math.min(...entitiesStore.entities.map(e => e.rating)))
})

const formatRelativeTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  return `${diffDays}d ago`
}

onMounted(() => {
  entitiesStore.refreshEntities()
  comparisonsStore.refreshData()
})
</script>
