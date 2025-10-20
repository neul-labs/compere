<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between">
      <div>
        <h1 class="h1 font-bold text-surface-900-50-token">Dashboard</h1>
        <p class="text-surface-600-300-token text-lg">
          Welcome to your comparative rating system overview
        </p>
      </div>

      <!-- Quick Actions -->
      <div class="flex items-center space-x-3 mt-4 lg:mt-0">
        <button
          @click="refreshData"
          :disabled="loading"
          class="btn variant-ghost-surface"
        >
          <i :class="['fas', loading ? 'fa-spinner fa-spin' : 'fa-sync-alt']"></i>
          <span class="hidden sm:inline ml-2">Refresh</span>
        </button>

        <router-link to="/compare" class="btn variant-filled-primary">
          <i class="fas fa-balance-scale"></i>
          <span class="hidden sm:inline ml-2">Start Comparing</span>
        </router-link>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatsCard
        title="Total Entities"
        :value="stats.totalEntities"
        icon="fas fa-database"
        color="primary"
        :loading="loading"
      />

      <StatsCard
        title="Total Comparisons"
        :value="stats.totalComparisons"
        icon="fas fa-balance-scale"
        color="secondary"
        :loading="loading"
      />

      <StatsCard
        title="Average Rating"
        :value="stats.averageRating"
        icon="fas fa-star"
        color="tertiary"
        :loading="loading"
      />

      <StatsCard
        title="Active Users"
        :value="stats.activeUsers"
        icon="fas fa-users"
        color="warning"
        :loading="loading"
      />
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Left Column -->
      <div class="lg:col-span-2 space-y-8">
        <!-- Quick Compare Section -->
        <div class="card p-6">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h2 class="h3 font-bold">Quick Compare</h2>
              <p class="text-surface-600-300-token">
                {{ hasMabSuggestion ? 'MAB Algorithm Suggestion' : 'Random Pair Selection' }}
              </p>
            </div>

            <div class="flex items-center space-x-2">
              <div
                :class="[
                  'w-3 h-3 rounded-full',
                  hasMabSuggestion ? 'bg-green-500' : 'bg-yellow-500'
                ]"
              ></div>
              <span class="text-sm font-medium">
                {{ hasMabSuggestion ? 'MAB Active' : 'MAB Inactive' }}
              </span>
            </div>
          </div>

          <!-- Comparison Cards -->
          <div v-if="comparison" class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <EntityComparisonCard
              :entity="comparison.entity1"
              @select="() => submitComparison(comparison.entity1.id)"
              :loading="submitting"
            />

            <EntityComparisonCard
              :entity="comparison.entity2"
              @select="() => submitComparison(comparison.entity2.id)"
              :loading="submitting"
            />
          </div>

          <!-- No Comparison Available -->
          <div v-else-if="!loading" class="text-center py-12">
            <i class="fas fa-exclamation-triangle text-6xl text-warning-500 mb-4"></i>
            <h3 class="h4 font-semibold mb-2">No Comparisons Available</h3>
            <p class="text-surface-600-300-token mb-4">
              You need at least 2 entities to start comparing.
            </p>
            <router-link to="/entities" class="btn variant-filled-primary">
              <i class="fas fa-plus"></i>
              <span class="ml-2">Add Entities</span>
            </router-link>
          </div>

          <!-- Loading State -->
          <div v-else class="flex justify-center py-12">
            <div class="flex flex-col items-center space-y-4">
              <div class="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
              <p class="text-surface-600-300-token">Loading comparison...</p>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="card p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="h3 font-bold">Recent Activity</h2>
            <router-link to="/analytics" class="btn variant-ghost-surface btn-sm">
              <span>View All</span>
              <i class="fas fa-arrow-right ml-2"></i>
            </router-link>
          </div>

          <div v-if="recentComparisons.length > 0" class="space-y-4">
            <div
              v-for="comparison in recentComparisons.slice(0, 5)"
              :key="comparison.id"
              class="flex items-center space-x-4 p-3 rounded-lg bg-surface-100-800-token"
            >
              <div class="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
                <i class="fas fa-balance-scale text-white"></i>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium truncate">
                  Comparison #{{ comparison.id }}
                </p>
                <p class="text-sm text-surface-600-300-token">
                  {{ formatRelativeTime(comparison.created_at) }}
                </p>
              </div>
              <div class="text-sm text-surface-600-300-token">
                <i class="fas fa-trophy text-warning-500"></i>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8">
            <i class="fas fa-history text-4xl text-surface-400-500-token mb-2"></i>
            <p class="text-surface-600-300-token">No recent activity</p>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="space-y-8">
        <!-- Top Rated Entities -->
        <div class="card p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="h3 font-bold">Leaderboard</h2>
            <router-link to="/leaderboard" class="btn variant-ghost-surface btn-sm">
              <span>View All</span>
              <i class="fas fa-arrow-right ml-2"></i>
            </router-link>
          </div>

          <div v-if="topEntities.length > 0" class="space-y-4">
            <div
              v-for="(entity, index) in topEntities.slice(0, 5)"
              :key="entity.id"
              class="flex items-center space-x-4"
            >
              <div class="flex-shrink-0">
                <div
                  :class="[
                    'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold',
                    getRankColor(index + 1)
                  ]"
                >
                  {{ index + 1 }}
                </div>
              </div>

              <div class="flex-1 min-w-0">
                <p class="font-medium truncate">{{ entity.name }}</p>
                <p class="text-sm text-surface-600-300-token">
                  Rating: {{ formatRating(entity.rating) }}
                </p>
              </div>

              <div :class="['text-lg font-bold', getRatingColor(entity.rating)]">
                <i class="fas fa-star"></i>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8">
            <i class="fas fa-trophy text-4xl text-surface-400-500-token mb-2"></i>
            <p class="text-surface-600-300-token">No entities yet</p>
          </div>
        </div>

        <!-- System Status -->
        <div class="card p-6">
          <h2 class="h3 font-bold mb-6">System Status</h2>

          <div class="space-y-4">
            <StatusItem
              label="API Connection"
              :status="apiStatus"
              icon="fas fa-server"
            />

            <StatusItem
              label="MAB Algorithm"
              :status="mabStatus"
              icon="fas fa-brain"
            />

            <StatusItem
              label="Rating System"
              status="active"
              icon="fas fa-star"
            />

            <StatusItem
              label="Database"
              status="active"
              icon="fas fa-database"
            />
          </div>

          <!-- System Info -->
          <div class="mt-6 pt-4 border-t border-surface-300-600-token">
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p class="text-surface-600-300-token">Version</p>
                <p class="font-medium">v0.1.0</p>
              </div>
              <div>
                <p class="text-surface-600-300-token">Uptime</p>
                <p class="font-medium">24h 35m</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useEntitiesStore } from '../stores/entities.js'
import { useComparisonsStore } from '../stores/comparisons.js'
import { formatRating, getRatingColor } from '../utils/simulation.js'

// Components
import StatsCard from '../components/StatsCard.vue'
import EntityComparisonCard from '../components/EntityComparisonCard.vue'
import StatusItem from '../components/StatusItem.vue'

const entitiesStore = useEntitiesStore()
const comparisonsStore = useComparisonsStore()

// State
const loading = ref(false)
const submitting = ref(false)

// Computed
const stats = computed(() => ({
  totalEntities: entitiesStore.entities.length,
  totalComparisons: comparisonsStore.comparisons.length,
  averageRating: comparisonsStore.stats.averageRating,
  activeUsers: 1 // Mock data
}))

const comparison = computed(() => comparisonsStore.mabSuggestion || comparisonsStore.nextComparison)
const hasMabSuggestion = computed(() => !!comparisonsStore.mabSuggestion)
const topEntities = computed(() => comparisonsStore.topRatedEntities)
const recentComparisons = computed(() => comparisonsStore.comparisonHistory)

const apiStatus = computed(() => 'active') // Would be determined by connection status
const mabStatus = computed(() => hasMabSuggestion.value ? 'active' : 'warning')

// Methods
const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      entitiesStore.refreshEntities(),
      comparisonsStore.refreshData()
    ])
  } catch (error) {
    window.showNotification?.('error', 'Refresh Failed', error.message)
  } finally {
    loading.value = false
  }
}

const submitComparison = async (winnerId) => {
  if (!comparison.value) return

  submitting.value = true
  try {
    const result = await comparisonsStore.submitComparison(
      comparison.value.entity1.id,
      comparison.value.entity2.id,
      winnerId
    )

    if (result.success) {
      window.showNotification?.('success', 'Comparison Submitted', 'Rating updated successfully')
    } else {
      window.showNotification?.('error', 'Submission Failed', result.error)
    }
  } catch (error) {
    window.showNotification?.('error', 'Submission Failed', error.message)
  } finally {
    submitting.value = false
  }
}

const getRankColor = (rank) => {
  if (rank === 1) return 'bg-yellow-500 text-white'
  if (rank === 2) return 'bg-gray-400 text-white'
  if (rank === 3) return 'bg-orange-600 text-white'
  return 'bg-surface-500-400-token text-white'
}

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

// Lifecycle
onMounted(async () => {
  await refreshData()
})
</script>