<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-surface-900">Dashboard</h1>
        <p class="text-surface-500 mt-1">
          Welcome to your comparative rating system overview
        </p>
      </div>

      <!-- Quick Actions -->
      <div class="flex items-center space-x-3 mt-4 lg:mt-0">
        <button
          @click="refreshData"
          :disabled="loading"
          class="btn btn-secondary"
        >
          <i :class="['fas', loading ? 'fa-spinner fa-spin' : 'fa-sync-alt']"></i>
          <span class="hidden sm:inline ml-2">Refresh</span>
        </button>

        <router-link to="/compare" class="btn btn-primary">
          <i class="fas fa-balance-scale"></i>
          <span class="hidden sm:inline ml-2">Start Comparing</span>
        </router-link>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-surface-500">Total Entities</p>
            <p class="text-3xl font-bold text-surface-900 mt-1">{{ stats.totalEntities }}</p>
          </div>
          <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-database text-primary-600 text-xl"></i>
          </div>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-surface-500">Total Comparisons</p>
            <p class="text-3xl font-bold text-surface-900 mt-1">{{ stats.totalComparisons }}</p>
          </div>
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-balance-scale text-green-600 text-xl"></i>
          </div>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-surface-500">Average Rating</p>
            <p class="text-3xl font-bold text-surface-900 mt-1">{{ stats.averageRating }}</p>
          </div>
          <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-star text-yellow-600 text-xl"></i>
          </div>
        </div>
      </div>

      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-surface-500">Active Users</p>
            <p class="text-3xl font-bold text-surface-900 mt-1">{{ stats.activeUsers }}</p>
          </div>
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <i class="fas fa-users text-purple-600 text-xl"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Left Column -->
      <div class="lg:col-span-2 space-y-8">
        <!-- Quick Compare Section -->
        <div class="card p-6">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h2 class="text-lg font-bold text-surface-900">Quick Compare</h2>
              <p class="text-surface-500 text-sm">
                {{ hasMabSuggestion ? 'MAB Algorithm Suggestion' : 'Random Pair Selection' }}
              </p>
            </div>

            <div class="flex items-center space-x-2">
              <div
                :class="[
                  'w-2 h-2 rounded-full',
                  hasMabSuggestion ? 'bg-green-500' : 'bg-yellow-500'
                ]"
              ></div>
              <span class="text-sm text-surface-600">
                {{ hasMabSuggestion ? 'MAB Active' : 'MAB Inactive' }}
              </span>
            </div>
          </div>

          <!-- Comparison Cards -->
          <div v-if="comparison" class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              @click="submitComparison(comparison.entity1.id)"
              class="card p-4 cursor-pointer hover:shadow-lg hover:border-primary-300 transition-all"
              :class="{ 'opacity-50 pointer-events-none': submitting }"
            >
              <div class="aspect-video bg-surface-100 rounded-lg mb-4 flex items-center justify-center overflow-hidden">
                <img
                  v-if="comparison.entity1.image_urls?.length"
                  :src="comparison.entity1.image_urls[0]"
                  :alt="comparison.entity1.name"
                  class="w-full h-full object-cover"
                />
                <i v-else class="fas fa-image text-4xl text-surface-300"></i>
              </div>
              <h3 class="font-semibold text-surface-900">{{ comparison.entity1.name }}</h3>
              <p class="text-sm text-surface-500 mt-1 line-clamp-2">{{ comparison.entity1.description }}</p>
              <div class="mt-3 flex items-center justify-between">
                <span class="badge badge-primary">Rating: {{ formatRating(comparison.entity1.rating) }}</span>
                <button class="btn btn-sm btn-primary">Select</button>
              </div>
            </div>

            <div
              @click="submitComparison(comparison.entity2.id)"
              class="card p-4 cursor-pointer hover:shadow-lg hover:border-primary-300 transition-all"
              :class="{ 'opacity-50 pointer-events-none': submitting }"
            >
              <div class="aspect-video bg-surface-100 rounded-lg mb-4 flex items-center justify-center overflow-hidden">
                <img
                  v-if="comparison.entity2.image_urls?.length"
                  :src="comparison.entity2.image_urls[0]"
                  :alt="comparison.entity2.name"
                  class="w-full h-full object-cover"
                />
                <i v-else class="fas fa-image text-4xl text-surface-300"></i>
              </div>
              <h3 class="font-semibold text-surface-900">{{ comparison.entity2.name }}</h3>
              <p class="text-sm text-surface-500 mt-1 line-clamp-2">{{ comparison.entity2.description }}</p>
              <div class="mt-3 flex items-center justify-between">
                <span class="badge badge-primary">Rating: {{ formatRating(comparison.entity2.rating) }}</span>
                <button class="btn btn-sm btn-primary">Select</button>
              </div>
            </div>
          </div>

          <!-- No Comparison Available -->
          <div v-else-if="!loading" class="text-center py-12">
            <i class="fas fa-exclamation-triangle text-5xl text-yellow-500 mb-4"></i>
            <h3 class="text-lg font-semibold text-surface-900 mb-2">No Comparisons Available</h3>
            <p class="text-surface-500 mb-4">
              You need at least 2 entities to start comparing.
            </p>
            <router-link to="/simulations" class="btn btn-primary">
              <i class="fas fa-play mr-2"></i>
              Load Sample Data
            </router-link>
          </div>

          <!-- Loading State -->
          <div v-else class="flex justify-center py-12">
            <div class="flex flex-col items-center space-y-4">
              <div class="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
              <p class="text-surface-500">Loading comparison...</p>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="card p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-bold text-surface-900">Recent Activity</h2>
            <router-link to="/analytics" class="text-sm text-primary-600 hover:text-primary-700">
              View All <i class="fas fa-arrow-right ml-1"></i>
            </router-link>
          </div>

          <div v-if="recentComparisons.length > 0" class="space-y-3">
            <div
              v-for="comp in recentComparisons.slice(0, 5)"
              :key="comp.id"
              class="flex items-center space-x-4 p-3 rounded-lg bg-surface-50"
            >
              <div class="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                <i class="fas fa-balance-scale text-primary-600"></i>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-surface-900 truncate">
                  Comparison #{{ comp.id }}
                </p>
                <p class="text-sm text-surface-500">
                  {{ formatRelativeTime(comp.created_at) }}
                </p>
              </div>
              <i class="fas fa-trophy text-yellow-500"></i>
            </div>
          </div>

          <div v-else class="text-center py-8">
            <i class="fas fa-history text-4xl text-surface-300 mb-2"></i>
            <p class="text-surface-500">No recent activity</p>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="space-y-8">
        <!-- Top Rated Entities -->
        <div class="card p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-bold text-surface-900">Leaderboard</h2>
            <router-link to="/leaderboard" class="text-sm text-primary-600 hover:text-primary-700">
              View All <i class="fas fa-arrow-right ml-1"></i>
            </router-link>
          </div>

          <div v-if="topEntities.length > 0" class="space-y-4">
            <div
              v-for="(entity, index) in topEntities.slice(0, 5)"
              :key="entity.id"
              class="flex items-center space-x-4"
            >
              <div
                :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold',
                  getRankColor(index + 1)
                ]"
              >
                {{ index + 1 }}
              </div>

              <div class="flex-1 min-w-0">
                <p class="font-medium text-surface-900 truncate">{{ entity.name }}</p>
                <p class="text-sm text-surface-500">
                  Rating: {{ formatRating(entity.rating) }}
                </p>
              </div>

              <i class="fas fa-star text-yellow-500"></i>
            </div>
          </div>

          <div v-else class="text-center py-8">
            <i class="fas fa-trophy text-4xl text-surface-300 mb-2"></i>
            <p class="text-surface-500">No entities yet</p>
          </div>
        </div>

        <!-- System Status -->
        <div class="card p-6">
          <h2 class="text-lg font-bold text-surface-900 mb-6">System Status</h2>

          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <i class="fas fa-server text-surface-400 w-5"></i>
                <span class="text-surface-700">API Connection</span>
              </div>
              <span class="badge badge-success">Active</span>
            </div>

            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <i class="fas fa-brain text-surface-400 w-5"></i>
                <span class="text-surface-700">MAB Algorithm</span>
              </div>
              <span :class="['badge', hasMabSuggestion ? 'badge-success' : 'badge-warning']">
                {{ hasMabSuggestion ? 'Active' : 'Inactive' }}
              </span>
            </div>

            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <i class="fas fa-star text-surface-400 w-5"></i>
                <span class="text-surface-700">Rating System</span>
              </div>
              <span class="badge badge-success">Active</span>
            </div>

            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <i class="fas fa-database text-surface-400 w-5"></i>
                <span class="text-surface-700">Database</span>
              </div>
              <span class="badge badge-success">Active</span>
            </div>
          </div>

          <!-- System Info -->
          <div class="mt-6 pt-4 border-t border-surface-200">
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p class="text-surface-500">Version</p>
                <p class="font-medium text-surface-900">v0.1.0</p>
              </div>
              <div>
                <p class="text-surface-500">Uptime</p>
                <p class="font-medium text-surface-900">24h 35m</p>
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

const entitiesStore = useEntitiesStore()
const comparisonsStore = useComparisonsStore()

// State
const loading = ref(false)
const submitting = ref(false)

// Computed
const stats = computed(() => ({
  totalEntities: entitiesStore.entities.length,
  totalComparisons: comparisonsStore.comparisons.length,
  averageRating: comparisonsStore.stats?.averageRating || 1500,
  activeUsers: 1
}))

const comparison = computed(() => comparisonsStore.mabSuggestion || comparisonsStore.nextComparison)
const hasMabSuggestion = computed(() => !!comparisonsStore.mabSuggestion)
const topEntities = computed(() => comparisonsStore.topRatedEntities || [])
const recentComparisons = computed(() => comparisonsStore.comparisonHistory || [])

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
  return 'bg-surface-400 text-white'
}

const formatRating = (rating) => {
  return Math.round(rating || 1500)
}

const formatRelativeTime = (dateString) => {
  if (!dateString) return 'Unknown'
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
