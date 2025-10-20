<template>
  <div class="space-y-8">
    <div class="text-center">
      <h1 class="h1 font-bold text-surface-900-50-token mb-4">Leaderboard</h1>
      <p class="text-surface-600-300-token text-lg">Rankings based on comparative analysis</p>
    </div>

    <div class="max-w-4xl mx-auto">
      <div class="card p-6">
        <div class="space-y-4">
          <div
            v-for="(entity, index) in rankedEntities"
            :key="entity.id"
            class="flex items-center space-x-6 p-4 rounded-lg bg-surface-100-800-token hover-lift"
          >
            <div
              :class="[
                'w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg',
                getRankColor(index + 1)
              ]"
            >
              {{ index + 1 }}
            </div>

            <div class="w-16 h-16 rounded-full bg-surface-300-600-token overflow-hidden">
              <img
                v-if="entity.image_urls?.[0]"
                :src="entity.image_urls[0]"
                :alt="entity.name"
                class="w-full h-full object-cover"
              >
              <div v-else class="w-full h-full flex items-center justify-center">
                <i class="fas fa-image text-surface-500-400-token"></i>
              </div>
            </div>

            <div class="flex-1">
              <h3 class="text-xl font-bold">{{ entity.name }}</h3>
              <p class="text-surface-600-300-token">{{ entity.description }}</p>
            </div>

            <div class="text-right">
              <p :class="['text-2xl font-bold', getRatingColor(entity.rating)]">
                {{ formatRating(entity.rating) }}
              </p>
              <p class="text-sm text-surface-500-400-token">Rating</p>
            </div>
          </div>
        </div>

        <div v-if="rankedEntities.length === 0" class="text-center py-12">
          <i class="fas fa-trophy text-6xl text-surface-400-500-token mb-4"></i>
          <h3 class="h3 font-bold mb-2">No Rankings Yet</h3>
          <p class="text-surface-600-300-token">Start comparing entities to see rankings</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useEntitiesStore } from '../stores/entities.js'
import { formatRating, getRatingColor } from '../utils/simulation.js'

const entitiesStore = useEntitiesStore()

const rankedEntities = computed(() => {
  return [...entitiesStore.entities].sort((a, b) => b.rating - a.rating)
})

const getRankColor = (rank) => {
  if (rank === 1) return 'bg-yellow-500'
  if (rank === 2) return 'bg-gray-400'
  if (rank === 3) return 'bg-orange-600'
  return 'bg-primary-500'
}

onMounted(() => {
  entitiesStore.refreshEntities()
})
</script>