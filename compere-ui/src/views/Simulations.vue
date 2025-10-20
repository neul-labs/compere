<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h1 class="h1 font-bold text-surface-900-50-token mb-4">Simulation Scenarios</h1>
      <p class="text-surface-600-300-token text-lg max-w-3xl mx-auto">
        Explore different use cases for the Compere rating system.
        Load pre-built scenarios and watch the MAB algorithm learn from comparisons.
      </p>
    </div>

    <!-- Simulation Controls -->
    <div class="max-w-4xl mx-auto">
      <div class="card p-6">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div class="flex items-center space-x-4">
            <div
              :class="[
                'w-4 h-4 rounded-full',
                isSimulationRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
              ]"
            ></div>
            <span class="font-semibold">
              {{ isSimulationRunning ? 'Simulation Running...' : 'Ready to Simulate' }}
            </span>
          </div>

          <div class="flex items-center space-x-3">
            <button
              @click="clearAll"
              :disabled="isSimulationRunning || entitiesStore.entities.length === 0"
              class="btn variant-ghost-error btn-sm"
            >
              <i class="fas fa-trash"></i>
              <span class="hidden sm:inline ml-2">Clear All</span>
            </button>

            <button
              @click="stopSimulation"
              v-if="isSimulationRunning"
              class="btn variant-filled-error"
            >
              <i class="fas fa-stop"></i>
              <span class="ml-2">Stop</span>
            </button>
          </div>
        </div>

        <!-- Progress Bar -->
        <div v-if="simulationProgress.total > 0" class="mt-4">
          <div class="flex justify-between text-sm text-surface-600-300-token mb-2">
            <span>Progress: {{ simulationProgress.completed }}/{{ simulationProgress.total }}</span>
            <span>{{ Math.round((simulationProgress.completed / simulationProgress.total) * 100) }}%</span>
          </div>
          <div class="w-full bg-surface-300-600-token rounded-full h-2">
            <div
              class="bg-primary-500 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${(simulationProgress.completed / simulationProgress.total) * 100}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Scenario Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
      <div
        v-for="(scenario, key) in simulationScenarios"
        :key="key"
        class="card p-6 hover-lift"
      >
        <!-- Scenario Header -->
        <div class="flex items-center space-x-4 mb-4">
          <div class="text-4xl">{{ scenario.icon }}</div>
          <div class="flex-1">
            <h2 class="h3 font-bold">{{ scenario.name }}</h2>
            <p class="text-surface-600-300-token">{{ scenario.description }}</p>
          </div>
        </div>

        <!-- Scenario Stats -->
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div class="text-center p-3 rounded-lg bg-surface-100-800-token">
            <p class="text-2xl font-bold text-primary-500">{{ scenario.entities.length }}</p>
            <p class="text-sm text-surface-600-300-token">Entities</p>
          </div>
          <div class="text-center p-3 rounded-lg bg-surface-100-800-token">
            <p class="text-2xl font-bold text-secondary-500">
              {{ getScenarioCategories(scenario).length }}
            </p>
            <p class="text-sm text-surface-600-300-token">Categories</p>
          </div>
        </div>

        <!-- Entity Preview -->
        <div class="mb-6">
          <h4 class="font-semibold mb-3">Sample Entities:</h4>
          <div class="space-y-2">
            <div
              v-for="entity in scenario.entities.slice(0, 3)"
              :key="entity.name"
              class="flex items-center space-x-3 p-2 rounded bg-surface-100-800-token"
            >
              <img
                v-if="entity.image_urls[0]"
                :src="entity.image_urls[0]"
                :alt="entity.name"
                class="w-8 h-8 rounded object-cover"
                @error="$event.target.style.display = 'none'"
              >
              <div class="w-8 h-8 bg-surface-300-600-token rounded flex items-center justify-center text-xs" v-else>
                {{ entity.name.charAt(0) }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium truncate">{{ entity.name }}</p>
                <p class="text-xs text-surface-600-300-token">{{ entity.category }}</p>
              </div>
            </div>
            <p v-if="scenario.entities.length > 3" class="text-xs text-surface-500-400-token text-center">
              +{{ scenario.entities.length - 3 }} more entities
            </p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="space-y-3">
          <button
            @click="loadScenario(key, scenario)"
            :disabled="isSimulationRunning"
            class="w-full btn variant-filled-primary"
          >
            <i class="fas fa-download"></i>
            <span class="ml-2">Load Scenario</span>
          </button>

          <div class="grid grid-cols-2 gap-3">
            <button
              @click="runQuickSimulation(key, scenario, 10)"
              :disabled="isSimulationRunning"
              class="btn variant-ghost-surface"
            >
              <i class="fas fa-play"></i>
              <span class="ml-2">Quick (10)</span>
            </button>

            <button
              @click="runFullSimulation(key, scenario, 50)"
              :disabled="isSimulationRunning"
              class="btn variant-ghost-secondary"
            >
              <i class="fas fa-fast-forward"></i>
              <span class="ml-2">Full (50)</span>
            </button>
          </div>
        </div>

        <!-- Scenario Status -->
        <div v-if="runningScenario === key" class="mt-4 p-3 rounded-lg bg-primary-100 dark:bg-primary-900">
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 bg-primary-500 rounded-full animate-pulse"></div>
            <span class="text-sm font-medium text-primary-700 dark:text-primary-300">
              Running {{ scenario.name }}...
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Current Results -->
    <div v-if="entitiesStore.entities.length > 0" class="max-w-6xl mx-auto">
      <div class="card p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="h3 font-bold">Current Results</h2>
          <div class="flex items-center space-x-4 text-sm text-surface-600-300-token">
            <span>{{ entitiesStore.entities.length }} entities</span>
            <span>{{ comparisonsStore.comparisons.length }} comparisons</span>
            <router-link to="/leaderboard" class="btn variant-ghost-surface btn-sm">
              <span>View Full Leaderboard</span>
              <i class="fas fa-arrow-right ml-2"></i>
            </router-link>
          </div>
        </div>

        <!-- Top 5 Leaderboard -->
        <div class="grid grid-cols-1 lg:grid-cols-5 gap-4">
          <div
            v-for="(entity, index) in topEntities.slice(0, 5)"
            :key="entity.id"
            class="text-center"
          >
            <div class="relative">
              <div class="w-20 h-20 mx-auto mb-3 rounded-full overflow-hidden bg-surface-200-700-token">
                <img
                  v-if="entity.image_urls && entity.image_urls[0]"
                  :src="entity.image_urls[0]"
                  :alt="entity.name"
                  class="w-full h-full object-cover"
                  @error="$event.target.style.display = 'none'"
                >
                <div v-else class="w-full h-full flex items-center justify-center text-surface-500-400-token">
                  <i class="fas fa-image text-2xl"></i>
                </div>
              </div>

              <!-- Rank Badge -->
              <div
                :class="[
                  'absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white',
                  getRankBadgeColor(index + 1)
                ]"
              >
                {{ index + 1 }}
              </div>
            </div>

            <h4 class="font-semibold truncate">{{ entity.name }}</h4>
            <p :class="['text-sm font-bold', getRatingColor(entity.rating)]">
              {{ formatRating(entity.rating) }}
            </p>
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
import { simulationScenarios, simulateComparisons, formatRating, getRatingColor } from '../utils/simulation.js'

const entitiesStore = useEntitiesStore()
const comparisonsStore = useComparisonsStore()

// State
const isSimulationRunning = ref(false)
const runningScenario = ref(null)
const simulationProgress = ref({ completed: 0, total: 0 })

// Computed
const topEntities = computed(() => {
  return [...entitiesStore.entities].sort((a, b) => b.rating - a.rating)
})

// Methods
const getScenarioCategories = (scenario) => {
  return [...new Set(scenario.entities.map(e => e.category))]
}

const getRankBadgeColor = (rank) => {
  if (rank === 1) return 'bg-yellow-500'  // Gold
  if (rank === 2) return 'bg-gray-400'    // Silver
  if (rank === 3) return 'bg-orange-600'  // Bronze
  return 'bg-primary-500'
}

const loadScenario = async (scenarioKey, scenario) => {
  if (isSimulationRunning.value) return

  try {
    // Clear existing data first
    await clearAll()

    // Create entities
    const results = []
    for (const entityData of scenario.entities) {
      const result = await entitiesStore.createEntity(entityData)
      if (result.success) {
        results.push(result.data)
      }
    }

    window.showNotification?.(
      'success',
      'Scenario Loaded',
      `${results.length} entities loaded for ${scenario.name}`
    )

    // Refresh data
    await refreshData()

  } catch (error) {
    window.showNotification?.('error', 'Load Failed', error.message)
  }
}

const runQuickSimulation = async (scenarioKey, scenario, comparisons = 10) => {
  await runSimulation(scenarioKey, scenario, comparisons)
}

const runFullSimulation = async (scenarioKey, scenario, comparisons = 50) => {
  await runSimulation(scenarioKey, scenario, comparisons)
}

const runSimulation = async (scenarioKey, scenario, comparisonCount) => {
  if (isSimulationRunning.value) return

  isSimulationRunning.value = true
  runningScenario.value = scenarioKey
  simulationProgress.value = { completed: 0, total: comparisonCount }

  try {
    // Load scenario first if no entities exist
    if (entitiesStore.entities.length === 0) {
      await loadScenario(scenarioKey, scenario)
    }

    // Run simulated comparisons
    for (let i = 0; i < comparisonCount; i++) {
      // Check if simulation was stopped
      if (!isSimulationRunning.value) break

      // Get entities for comparison
      const entities = entitiesStore.entities
      if (entities.length < 2) break

      // Pick random entities
      const entity1 = entities[Math.floor(Math.random() * entities.length)]
      let entity2 = entities[Math.floor(Math.random() * entities.length)]
      while (entity2.id === entity1.id && entities.length > 1) {
        entity2 = entities[Math.floor(Math.random() * entities.length)]
      }

      // Simulate comparison result (with some intelligence based on current ratings)
      const ratingDiff = entity1.rating - entity2.rating
      const probability1Wins = 1 / (1 + Math.pow(10, -ratingDiff / 400))
      const winner = Math.random() < probability1Wins ? entity1 : entity2

      // Submit comparison
      await comparisonsStore.createComparison({
        entity1_id: entity1.id,
        entity2_id: entity2.id,
        selected_entity_id: winner.id
      })

      simulationProgress.value.completed = i + 1

      // Small delay to see progress
      await new Promise(resolve => setTimeout(resolve, 100))
    }

    // Refresh all data
    await refreshData()

    window.showNotification?.(
      'success',
      'Simulation Complete',
      `${simulationProgress.value.completed} comparisons completed`
    )

  } catch (error) {
    window.showNotification?.('error', 'Simulation Failed', error.message)
  } finally {
    isSimulationRunning.value = false
    runningScenario.value = null
    simulationProgress.value = { completed: 0, total: 0 }
  }
}

const stopSimulation = () => {
  isSimulationRunning.value = false
  runningScenario.value = null
  window.showNotification?.('info', 'Simulation Stopped', 'Simulation was manually stopped')
}

const clearAll = async () => {
  if (isSimulationRunning.value) return

  try {
    // Clear entities (this should cascade to comparisons)
    const entities = [...entitiesStore.entities]
    for (const entity of entities) {
      await entitiesStore.deleteEntity(entity.id)
    }

    // Clear local state
    entitiesStore.entities = []
    comparisonsStore.comparisons = []

    window.showNotification?.('info', 'Data Cleared', 'All entities and comparisons removed')

  } catch (error) {
    window.showNotification?.('error', 'Clear Failed', error.message)
  }
}

const refreshData = async () => {
  await Promise.all([
    entitiesStore.refreshEntities(),
    comparisonsStore.refreshData()
  ])
}

// Lifecycle
onMounted(async () => {
  await refreshData()
})
</script>