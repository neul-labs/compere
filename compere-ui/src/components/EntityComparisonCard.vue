<template>
  <div
    class="card p-6 cursor-pointer transform transition-all duration-200 hover:scale-105 hover:shadow-xl"
    :class="{ 'opacity-50': loading }"
    @click="!loading && $emit('select')"
  >
    <!-- Entity Image -->
    <div class="relative mb-4">
      <div class="w-full h-48 bg-surface-200 rounded-lg overflow-hidden">
        <img
          v-if="entity.image_urls && entity.image_urls[0]"
          :src="entity.image_urls[0]"
          :alt="entity.name"
          class="w-full h-full object-cover"
          @error="imageError = true"
        >
        <div
          v-else
          class="w-full h-full flex items-center justify-center text-surface-400"
        >
          <i class="fas fa-image text-4xl" />
        </div>
      </div>

      <!-- Rating Badge -->
      <div class="absolute top-3 right-3">
        <div
          :class="[
            'px-3 py-1 rounded-full text-sm font-bold text-white shadow-lg',
            getRatingBadgeColor(entity.rating)
          ]"
        >
          {{ formatRating(entity.rating) }}
        </div>
      </div>

      <!-- Selection Indicator -->
      <div
        v-if="loading"
        class="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg"
      >
        <div class="w-8 h-8 border-4 border-white border-t-transparent rounded-full animate-spin" />
      </div>
    </div>

    <!-- Entity Details -->
    <div class="space-y-3">
      <div>
        <h3 class="text-xl font-bold text-surface-900 truncate">
          {{ entity.name }}
        </h3>
        <p class="text-surface-500 text-sm line-clamp-2">
          {{ entity.description }}
        </p>
      </div>

      <!-- Metadata -->
      <div class="flex items-center justify-between text-sm">
        <div class="flex items-center space-x-2 text-surface-400">
          <i class="fas fa-star" />
          <span>Rating</span>
        </div>
        <div :class="['font-bold', getRatingColor(entity.rating)]">
          {{ formatRating(entity.rating) }}
        </div>
      </div>

      <!-- Action Button -->
      <button
        :disabled="loading"
        class="w-full btn btn-primary mt-4"
      >
        <i
          v-if="loading"
          class="fas fa-spinner fa-spin"
        />
        <i
          v-else
          class="fas fa-hand-pointer"
        />
        <span class="ml-2">{{ loading ? 'Selecting...' : 'Choose This' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { formatRating, getRatingColor } from '../utils/simulation.js'

defineProps({
  entity: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['select'])

const imageError = ref(false)

const getRatingBadgeColor = (rating) => {
  if (rating >= 1600) return 'bg-green-500'
  if (rating >= 1500) return 'bg-yellow-500'
  if (rating >= 1400) return 'bg-orange-500'
  return 'bg-red-500'
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
