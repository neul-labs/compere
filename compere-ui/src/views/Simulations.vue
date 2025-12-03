<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-2xl font-bold text-surface-900 mb-2">Simulation Scenarios</h1>
      <p class="text-surface-500 max-w-2xl mx-auto">
        Load pre-built scenarios to explore the Compere rating system.
        Watch the MAB algorithm learn from comparisons.
      </p>
    </div>

    <!-- Simulation Controls -->
    <div class="max-w-4xl mx-auto">
      <div class="card p-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div class="flex items-center space-x-3">
            <div
              :class="[
                'w-3 h-3 rounded-full',
                isSimulationRunning ? 'bg-green-500 animate-pulse' : 'bg-surface-300'
              ]"
            ></div>
            <span class="font-medium text-surface-700">
              {{ isSimulationRunning ? 'Simulation Running...' : 'Ready to Simulate' }}
            </span>
          </div>

          <div class="flex items-center space-x-3">
            <button
              @click="clearAll"
              :disabled="isSimulationRunning || entitiesStore.entities.length === 0"
              class="btn btn-sm btn-danger"
            >
              <i class="fas fa-trash mr-2"></i>
              Clear All
            </button>

            <button
              v-if="isSimulationRunning"
              @click="stopSimulation"
              class="btn btn-danger"
            >
              <i class="fas fa-stop mr-2"></i>
              Stop
            </button>
          </div>
        </div>

        <!-- Progress Bar -->
        <div v-if="simulationProgress.total > 0" class="mt-4">
          <div class="flex justify-between text-sm text-surface-500 mb-2">
            <span>Progress: {{ simulationProgress.completed }}/{{ simulationProgress.total }}</span>
            <span>{{ Math.round((simulationProgress.completed / simulationProgress.total) * 100) }}%</span>
          </div>
          <div class="w-full bg-surface-200 rounded-full h-2">
            <div
              class="bg-primary-500 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${(simulationProgress.completed / simulationProgress.total) * 100}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Scenario Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
      <div
        v-for="(scenario, key) in simulationScenarios"
        :key="key"
        class="card p-6 hover-lift"
      >
        <!-- Scenario Header -->
        <div class="flex items-center space-x-4 mb-4">
          <div class="text-4xl">{{ scenario.icon }}</div>
          <div class="flex-1">
            <h2 class="text-lg font-bold text-surface-900">{{ scenario.name }}</h2>
            <p class="text-sm text-surface-500">{{ scenario.description }}</p>
          </div>
        </div>

        <!-- Scenario Stats -->
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div class="text-center p-3 rounded-lg bg-surface-50">
            <p class="text-2xl font-bold text-primary-600">{{ scenario.entities.length }}</p>
            <p class="text-xs text-surface-500">Entities</p>
          </div>
          <div class="text-center p-3 rounded-lg bg-surface-50">
            <p class="text-2xl font-bold text-green-600">
              {{ getScenarioCategories(scenario).length }}
            </p>
            <p class="text-xs text-surface-500">Categories</p>
          </div>
        </div>

        <!-- Entity Preview -->
        <div class="mb-4">
          <h4 class="text-sm font-medium text-surface-700 mb-2">Sample Entities:</h4>
          <div class="space-y-2">
            <div
              v-for="entity in scenario.entities.slice(0, 3)"
              :key="entity.name"
              class="flex items-center space-x-3 p-2 rounded bg-surface-50"
            >
              <img
                v-if="entity.image_urls[0]"
                :src="entity.image_urls[0]"
                :alt="entity.name"
                class="w-8 h-8 rounded object-cover"
                @error="$event.target.style.display = 'none'"
              >
              <div v-else class="w-8 h-8 bg-surface-200 rounded flex items-center justify-center text-xs font-medium text-surface-500">
                {{ entity.name.charAt(0) }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-surface-900 truncate">{{ entity.name }}</p>
              </div>
            </div>
            <p v-if="scenario.entities.length > 3" class="text-xs text-surface-400 text-center">
              +{{ scenario.entities.length - 3 }} more entities
            </p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="space-y-3">
          <button
            @click="loadScenario(key, scenario)"
            :disabled="isSimulationRunning"
            class="w-full btn btn-primary"
          >
            <i class="fas fa-download mr-2"></i>
            Load Scenario
          </button>

          <div class="grid grid-cols-2 gap-3">
            <button
              @click="runQuickSimulation(key, scenario, 10)"
              :disabled="isSimulationRunning"
              class="btn btn-secondary btn-sm"
            >
              <i class="fas fa-play mr-1"></i>
              Quick (10)
            </button>

            <button
              @click="runFullSimulation(key, scenario, 50)"
              :disabled="isSimulationRunning"
              class="btn btn-secondary btn-sm"
            >
              <i class="fas fa-fast-forward mr-1"></i>
              Full (50)
            </button>
          </div>
        </div>

        <!-- Running Indicator -->
        <div v-if="runningScenario === key" class="mt-4 p-3 rounded-lg bg-primary-50 border border-primary-200">
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
            <span class="text-sm font-medium text-primary-700">
              Running {{ scenario.name }}...
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Current Results -->
    <div v-if="entitiesStore.entities.length > 0" class="max-w-5xl mx-auto">
      <div class="card p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-bold text-surface-900">Current Results</h2>
          <div class="flex items-center space-x-4 text-sm text-surface-500">
            <span>{{ entitiesStore.entities.length }} entities</span>
            <span>{{ comparisonsStore.comparisons.length }} comparisons</span>
            <router-link to="/leaderboard" class="text-primary-600 hover:text-primary-700">
              View Leaderboard <i class="fas fa-arrow-right ml-1"></i>
            </router-link>
          </div>
        </div>

        <!-- Top 5 -->
        <div class="grid grid-cols-2 sm:grid-cols-5 gap-4">
          <div
            v-for="(entity, index) in topEntities.slice(0, 5)"
            :key="entity.id"
            class="text-center"
          >
            <div class="relative inline-block mb-2">
              <div class="w-16 h-16 rounded-full overflow-hidden bg-surface-100 mx-auto">
                <img
                  v-if="entity.image_urls && entity.image_urls[0]"
                  :src="entity.image_urls[0]"
                  :alt="entity.name"
                  class="w-full h-full object-cover"
                >
                <div v-else class="w-full h-full flex items-center justify-center">
                  <i class="fas fa-image text-surface-300"></i>
                </div>
              </div>
              <div
                :class="[
                  'absolute -top-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white',
                  getRankBadgeColor(index + 1)
                ]"
              >
                {{ index + 1 }}
              </div>
            </div>
            <h4 class="text-sm font-medium text-surface-900 truncate">{{ entity.name }}</h4>
            <p class="text-xs text-primary-600 font-semibold">{{ formatRating(entity.rating) }}</p>
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
import { simulationScenarios } from '../utils/simulation.js'

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
  if (rank === 1) return 'bg-yellow-500'
  if (rank === 2) return 'bg-gray-400'
  if (rank === 3) return 'bg-orange-600'
  return 'bg-primary-500'
}

const formatRating = (rating) => {
  return Math.round(rating || 1500)
}

const loadScenario = async (scenarioKey, scenario) => {
  if (isSimulationRunning.value) return

  try {
    await clearAll()

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
    if (entitiesStore.entities.length === 0) {
      await loadScenario(scenarioKey, scenario)
    }

    for (let i = 0; i < comparisonCount; i++) {
      if (!isSimulationRunning.value) break

      const entities = entitiesStore.entities
      if (entities.length < 2) break

      const entity1 = entities[Math.floor(Math.random() * entities.length)]
      let entity2 = entities[Math.floor(Math.random() * entities.length)]
      while (entity2.id === entity1.id && entities.length > 1) {
        entity2 = entities[Math.floor(Math.random() * entities.length)]
      }

      const ratingDiff = entity1.rating - entity2.rating
      const probability1Wins = 1 / (1 + Math.pow(10, -ratingDiff / 400))
      const winner = Math.random() < probability1Wins ? entity1 : entity2

      await comparisonsStore.createComparison({
        entity1_id: entity1.id,
        entity2_id: entity2.id,
        selected_entity_id: winner.id
      })

      simulationProgress.value.completed = i + 1
      await new Promise(resolve => setTimeout(resolve, 100))
    }

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
    const entities = [...entitiesStore.entities]
    for (const entity of entities) {
      await entitiesStore.deleteEntity(entity.id)
    }

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

onMounted(async () => {
  await refreshData()
})
</script>
