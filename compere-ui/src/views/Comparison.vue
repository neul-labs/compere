<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h1 class="h1 font-bold text-surface-900-50-token mb-4">Entity Comparison</h1>
      <p class="text-surface-600-300-token text-lg max-w-2xl mx-auto">
        Compare entities head-to-head to improve their ratings.
        {{ hasMabSuggestion ? 'Using MAB algorithm for intelligent pairing.' : 'Using similarity-based pairing.' }}
      </p>
    </div>

    <!-- Comparison Progress -->
    <div class="max-w-4xl mx-auto">
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center space-x-3">
            <div
              :class="[
                'w-4 h-4 rounded-full',
                hasMabSuggestion ? 'bg-green-500' : 'bg-yellow-500'
              ]"
            ></div>
            <span class="font-semibold">
              {{ hasMabSuggestion ? 'MAB Algorithm Active' : 'Similarity-Based Selection' }}
            </span>
          </div>

          <div class="flex items-center space-x-4">
            <div class="text-sm text-surface-600-300-token">
              <span class="font-medium">{{ comparisonCount }}</span> comparisons today
            </div>

            <button
              @click="getNewComparison"
              :disabled="loading"
              class="btn variant-ghost-surface btn-sm"
            >
              <i :class="['fas', loading ? 'fa-spinner fa-spin' : 'fa-sync-alt']"></i>
              <span class="ml-2">New Pair</span>
            </button>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="w-full bg-surface-300-600-token rounded-full h-2">
          <div
            class="bg-primary-500 h-2 rounded-full transition-all duration-300"
            :style="{ width: `${Math.min(comparisonCount * 5, 100)}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Comparison Interface -->
    <div class="max-w-6xl mx-auto">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-surface-600-300-token">Loading comparison...</p>
      </div>

      <!-- No Comparison Available -->
      <div v-else-if="!comparison" class="text-center py-16">
        <i class="fas fa-exclamation-triangle text-6xl text-warning-500 mb-6"></i>
        <h2 class="h2 font-bold mb-4">No Comparisons Available</h2>
        <p class="text-surface-600-300-token text-lg mb-8">
          You need at least 2 entities to start comparing.
        </p>
        <router-link to="/entities" class="btn variant-filled-primary">
          <i class="fas fa-plus"></i>
          <span class="ml-2">Add Entities</span>
        </router-link>
      </div>

      <!-- Comparison Cards -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Entity 1 -->
        <div class="space-y-4">
          <div class="text-center">
            <h3 class="h3 font-bold text-primary-500 mb-2">Option A</h3>
            <div class="h-1 bg-primary-500 rounded-full w-16 mx-auto"></div>
          </div>

          <EntityComparisonCard
            :entity="comparison.entity1"
            @select="() => submitComparison(comparison.entity1.id)"
            :loading="submitting && selectedWinner === comparison.entity1.id"
          />
        </div>

        <!-- VS Divider -->
        <div class="hidden lg:flex items-center justify-center">
          <div class="flex flex-col items-center space-y-4">
            <div class="w-16 h-16 bg-surface-300-600-token rounded-full flex items-center justify-center">
              <span class="text-2xl font-bold text-surface-600-300-token">VS</span>
            </div>
            <div class="w-px h-32 bg-surface-300-600-token"></div>
          </div>
        </div>

        <!-- Entity 2 -->
        <div class="space-y-4">
          <div class="text-center">
            <h3 class="h3 font-bold text-secondary-500 mb-2">Option B</h3>
            <div class="h-1 bg-secondary-500 rounded-full w-16 mx-auto"></div>
          </div>

          <EntityComparisonCard
            :entity="comparison.entity2"
            @select="() => submitComparison(comparison.entity2.id)"
            :loading="submitting && selectedWinner === comparison.entity2.id"
          />
        </div>
      </div>

      <!-- Mobile VS Divider -->
      <div class="lg:hidden flex justify-center py-6">
        <div class="w-12 h-12 bg-surface-300-600-token rounded-full flex items-center justify-center">
          <span class="text-xl font-bold text-surface-600-300-token">VS</span>
        </div>
      </div>

      <!-- Quick Actions -->
      <div v-if="comparison && !submitting" class="flex justify-center mt-8">
        <div class="flex items-center space-x-4">
          <button
            @click="submitTie"
            class="btn variant-ghost-surface"
          >
            <i class="fas fa-equals"></i>
            <span class="ml-2">It's a Tie</span>
          </button>

          <button
            @click="skipComparison"
            class="btn variant-ghost-surface"
          >
            <i class="fas fa-forward"></i>
            <span class="ml-2">Skip This Pair</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Recent Comparisons -->
    <div class="max-w-4xl mx-auto" v-if="recentComparisons.length > 0">
      <div class="card p-6">
        <h2 class="h3 font-bold mb-6">Recent Comparisons</h2>

        <div class="space-y-4">
          <div
            v-for="comparison in recentComparisons.slice(0, 3)"
            :key="comparison.id"
            class="flex items-center space-x-4 p-4 rounded-lg bg-surface-100-800-token"
          >
            <div class="w-12 h-12 bg-success-500 rounded-full flex items-center justify-center">
              <i class="fas fa-check text-white"></i>
            </div>

            <div class="flex-1">
              <p class="font-semibold">
                Comparison #{{ comparison.id }} completed
              </p>
              <p class="text-sm text-surface-600-300-token">
                {{ formatRelativeTime(comparison.created_at) }}
              </p>
            </div>

            <div class="flex items-center space-x-2">
              <i class="fas fa-trophy text-warning-500"></i>
              <span class="text-sm text-surface-600-300-token">
                Winner selected
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useComparisonsStore } from '../stores/comparisons.js'
import EntityComparisonCard from '../components/EntityComparisonCard.vue'

const comparisonsStore = useComparisonsStore()

// State
const loading = ref(false)
const submitting = ref(false)
const selectedWinner = ref(null)

// Computed
const comparison = computed(() =>
  comparisonsStore.mabSuggestion || comparisonsStore.nextComparison
)
const hasMabSuggestion = computed(() => !!comparisonsStore.mabSuggestion)
const comparisonCount = computed(() => comparisonsStore.comparisons.length)
const recentComparisons = computed(() =>
  comparisonsStore.comparisonHistory.slice(0, 5)
)

// Methods
const getNewComparison = async () => {
  loading.value = true
  try {
    await comparisonsStore.getMabSuggestion()
    if (!comparisonsStore.mabSuggestion) {
      await comparisonsStore.getNextComparison()
    }
  } catch (error) {
    window.showNotification?.('error', 'Error', 'Failed to get new comparison')
  } finally {
    loading.value = false
  }
}

const submitComparison = async (winnerId) => {
  if (!comparison.value || submitting.value) return

  selectedWinner.value = winnerId
  submitting.value = true

  try {
    const result = await comparisonsStore.submitComparison(
      comparison.value.entity1.id,
      comparison.value.entity2.id,
      winnerId
    )

    if (result.success) {
      window.showNotification?.(
        'success',
        'Comparison Submitted!',
        'Ratings have been updated'
      )

      // Automatically get next comparison
      await getNewComparison()
    } else {
      window.showNotification?.('error', 'Submission Failed', result.error)
    }
  } catch (error) {
    window.showNotification?.('error', 'Submission Failed', error.message)
  } finally {
    submitting.value = false
    selectedWinner.value = null
  }
}

const submitTie = async () => {
  if (!comparison.value) return

  // For ties, we can randomly select one or use a specific tie-handling logic
  const randomWinner = Math.random() > 0.5
    ? comparison.value.entity1.id
    : comparison.value.entity2.id

  await submitComparison(randomWinner)

  window.showNotification?.(
    'info',
    'Tie Recorded',
    'Both entities receive equal rating adjustment'
  )
}

const skipComparison = async () => {
  await getNewComparison()
  window.showNotification?.('info', 'Comparison Skipped', 'New pair loaded')
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
  await getNewComparison()
})
</script>