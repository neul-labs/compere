<template>
  <div class="flex items-center space-x-2">
    <!-- Connection Status Indicator -->
    <div
      :class="[
        'w-3 h-3 rounded-full transition-all duration-300',
        isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
      ]"
    ></div>

    <!-- Status Text -->
    <span
      :class="[
        'text-sm font-medium hidden sm:inline',
        isConnected ? 'text-green-600' : 'text-red-600'
      ]"
    >
      {{ statusText }}
    </span>

    <!-- Retry Button (when disconnected) -->
    <button
      v-if="!isConnected"
      @click="checkConnection"
      :disabled="checking"
      class="btn btn-sm btn-ghost"
      title="Retry Connection"
    >
      <i :class="['fas', checking ? 'fa-spinner fa-spin' : 'fa-sync-alt']"></i>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { healthApi } from '../services/api.js'

// State
const isConnected = ref(false)
const checking = ref(false)
const lastCheck = ref(null)

// Computed
const statusText = computed(() => {
  if (checking.value) return 'Checking...'
  if (isConnected.value) return 'Connected'
  return 'Disconnected'
})

// Methods
const checkConnection = async () => {
  try {
    checking.value = true
    await healthApi.check()
    isConnected.value = true
    lastCheck.value = new Date()
  } catch (error) {
    isConnected.value = false
    console.warn('Connection check failed:', error.message)
  } finally {
    checking.value = false
  }
}

// Auto-check connection periodically
let intervalId = null

onMounted(async () => {
  await checkConnection()

  // Check every 30 seconds
  intervalId = setInterval(checkConnection, 30000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})

// Expose for parent components
defineExpose({
  isConnected,
  checkConnection
})
</script>
