<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-2xl font-bold text-surface-900 mb-2">
        Entity Comparison
      </h1>
      <p class="text-surface-500 max-w-xl mx-auto">
        Compare entities head-to-head to improve their ratings.
        {{ hasMabSuggestion ? 'Using MAB algorithm for intelligent pairing.' : 'Using similarity-based pairing.' }}
      </p>
    </div>

    <!-- Status Bar -->
    <div class="max-w-3xl mx-auto">
      <div class="card p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div
              :class="[
                'w-2 h-2 rounded-full',
                hasMabSuggestion ? 'bg-green-500' : 'bg-yellow-500'
              ]"
            />
            <span class="text-sm text-surface-600">
              {{ hasMabSuggestion ? 'MAB Algorithm Active' : 'Similarity-Based Selection' }}
            </span>
          </div>

          <div class="flex items-center space-x-4">
            <span class="text-sm text-surface-500">{{ comparisonCount }} comparisons</span>
            <button
              :disabled="loading"
              class="btn btn-sm btn-secondary"
              @click="getNewComparison"
            >
              <i :class="['fas', loading ? 'fa-spinner fa-spin' : 'fa-sync-alt']" />
              <span class="ml-2">New Pair</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Comparison Interface -->
    <div class="max-w-4xl mx-auto">
      <!-- Loading -->
      <div
        v-if="loading"
        class="text-center py-16"
      >
        <div class="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p class="text-surface-500">
          Loading comparison...
        </p>
      </div>

      <!-- No Comparison -->
      <div
        v-else-if="!comparison"
        class="text-center py-16"
      >
        <i class="fas fa-exclamation-triangle text-5xl text-yellow-500 mb-4" />
        <h2 class="text-xl font-bold text-surface-900 mb-2">
          No Comparisons Available
        </h2>
        <p class="text-surface-500 mb-6">
          You need at least 2 entities to start comparing.
        </p>
        <router-link
          to="/simulations"
          class="btn btn-primary"
        >
          <i class="fas fa-play mr-2" />
          Load Sample Data
        </router-link>
      </div>

      <!-- Comparison Cards -->
      <div
        v-else
        class="grid grid-cols-1 md:grid-cols-2 gap-8"
      >
        <!-- Entity 1 -->
        <div
          class="card p-6 cursor-pointer hover:shadow-lg hover:border-primary-300 transition-all"
          :class="{ 'opacity-50 pointer-events-none': submitting }"
          @click="submitComparison(comparison.entity1.id)"
        >
          <div class="text-center mb-4">
            <span class="badge badge-primary">Option A</span>
          </div>
          <div class="aspect-video bg-surface-100 rounded-lg mb-4 overflow-hidden">
            <img
              v-if="comparison.entity1.image_urls?.length"
              :src="comparison.entity1.image_urls[0]"
              :alt="comparison.entity1.name"
              class="w-full h-full object-cover"
            >
            <div
              v-else
              class="w-full h-full flex items-center justify-center"
            >
              <i class="fas fa-image text-4xl text-surface-300" />
            </div>
          </div>
          <h3 class="text-lg font-bold text-surface-900 text-center">
            {{ comparison.entity1.name }}
          </h3>
          <p class="text-sm text-surface-500 text-center mt-1 line-clamp-2">
            {{ comparison.entity1.description }}
          </p>
          <div class="mt-4 text-center">
            <span class="text-primary-600 font-semibold">Rating: {{ Math.round(comparison.entity1.rating) }}</span>
          </div>
          <button class="btn btn-primary w-full mt-4">
            Select This One
          </button>
        </div>

        <!-- Entity 2 -->
        <div
          class="card p-6 cursor-pointer hover:shadow-lg hover:border-green-300 transition-all"
          :class="{ 'opacity-50 pointer-events-none': submitting }"
          @click="submitComparison(comparison.entity2.id)"
        >
          <div class="text-center mb-4">
            <span class="badge badge-success">Option B</span>
          </div>
          <div class="aspect-video bg-surface-100 rounded-lg mb-4 overflow-hidden">
            <img
              v-if="comparison.entity2.image_urls?.length"
              :src="comparison.entity2.image_urls[0]"
              :alt="comparison.entity2.name"
              class="w-full h-full object-cover"
            >
            <div
              v-else
              class="w-full h-full flex items-center justify-center"
            >
              <i class="fas fa-image text-4xl text-surface-300" />
            </div>
          </div>
          <h3 class="text-lg font-bold text-surface-900 text-center">
            {{ comparison.entity2.name }}
          </h3>
          <p class="text-sm text-surface-500 text-center mt-1 line-clamp-2">
            {{ comparison.entity2.description }}
          </p>
          <div class="mt-4 text-center">
            <span class="text-green-600 font-semibold">Rating: {{ Math.round(comparison.entity2.rating) }}</span>
          </div>
          <button class="btn bg-green-600 text-white hover:bg-green-700 w-full mt-4">
            Select This One
          </button>
        </div>
      </div>

      <!-- Skip Button -->
      <div
        v-if="comparison && !submitting"
        class="flex justify-center mt-6"
      >
        <button
          class="btn btn-ghost"
          @click="skipComparison"
        >
          <i class="fas fa-forward mr-2" />
          Skip This Pair
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useComparisonsStore } from '../stores/comparisons.js'

const comparisonsStore = useComparisonsStore()

const loading = ref(false)
const submitting = ref(false)

const comparison = computed(() => comparisonsStore.mabSuggestion || comparisonsStore.nextComparison)
const hasMabSuggestion = computed(() => !!comparisonsStore.mabSuggestion)
const comparisonCount = computed(() => comparisonsStore.comparisons.length)

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

  submitting.value = true
  try {
    const result = await comparisonsStore.submitComparison(
      comparison.value.entity1.id,
      comparison.value.entity2.id,
      winnerId
    )

    if (result.success) {
      window.showNotification?.('success', 'Comparison Submitted!', 'Ratings have been updated')
      await getNewComparison()
    } else {
      window.showNotification?.('error', 'Submission Failed', result.error)
    }
  } catch (error) {
    window.showNotification?.('error', 'Submission Failed', error.message)
  } finally {
    submitting.value = false
  }
}

const skipComparison = async () => {
  await getNewComparison()
  window.showNotification?.('info', 'Skipped', 'New pair loaded')
}

onMounted(async () => {
  await getNewComparison()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
