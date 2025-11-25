<template>
  <div class="space-y-8">
    <div class="text-center">
      <h1 class="text-2xl font-bold text-surface-900 mb-2">Leaderboard</h1>
      <p class="text-surface-500">Rankings based on comparative analysis</p>
    </div>

    <div class="max-w-3xl mx-auto">
      <div class="card p-6">
        <div v-if="rankedEntities.length > 0" class="space-y-4">
          <div
            v-for="(entity, index) in rankedEntities"
            :key="entity.id"
            class="flex items-center space-x-4 p-4 rounded-lg bg-surface-50 hover-lift"
          >
            <div
              :class="[
                'w-10 h-10 rounded-full flex items-center justify-center text-white font-bold',
                getRankColor(index + 1)
              ]"
            >
              {{ index + 1 }}
            </div>

            <div class="w-14 h-14 rounded-full bg-surface-200 overflow-hidden flex-shrink-0">
              <img
                v-if="entity.image_urls?.[0]"
                :src="entity.image_urls[0]"
                :alt="entity.name"
                class="w-full h-full object-cover"
              >
              <div v-else class="w-full h-full flex items-center justify-center">
                <i class="fas fa-image text-surface-400"></i>
              </div>
            </div>

            <div class="flex-1 min-w-0">
              <h3 class="font-bold text-surface-900 truncate">{{ entity.name }}</h3>
              <p class="text-sm text-surface-500 truncate">{{ entity.description }}</p>
            </div>

            <div class="text-right">
              <p class="text-xl font-bold text-primary-600">{{ formatRating(entity.rating) }}</p>
              <p class="text-xs text-surface-400">Rating</p>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-12">
          <i class="fas fa-trophy text-5xl text-surface-300 mb-4"></i>
          <h3 class="text-lg font-bold text-surface-900 mb-2">No Rankings Yet</h3>
          <p class="text-surface-500">Start comparing entities to see rankings</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useEntitiesStore } from '../stores/entities.js'

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

const formatRating = (rating) => Math.round(rating || 1500)

onMounted(() => {
  entitiesStore.refreshEntities()
})
</script>
