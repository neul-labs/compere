<template>
  <div
    id="app"
    class="min-h-screen bg-surface-100"
  >
    <!-- App Layout -->
    <div class="flex min-h-screen">
      <!-- Navigation Sidebar (desktop) -->
      <aside class="hidden lg:flex flex-shrink-0">
        <Navigation />
      </aside>

      <!-- Main Content Area -->
      <div class="flex-1 flex flex-col min-w-0 max-h-screen overflow-hidden">
        <!-- Header -->
        <header class="bg-white border-b border-surface-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div class="flex items-center space-x-4">
            <button
              class="btn btn-ghost btn-sm lg:hidden"
              @click="drawerOpen = !drawerOpen"
            >
              <i class="fas fa-bars text-lg" />
            </button>
            <h1 class="text-xl font-semibold text-surface-900">
              Compere
            </h1>
          </div>
          <div class="flex items-center space-x-4">
            <!-- Connection Status -->
            <div class="flex items-center space-x-2">
              <div
                :class="[
                  'w-2 h-2 rounded-full',
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                ]"
              />
              <span class="text-sm text-surface-600">
                {{ isConnected ? 'Connected' : 'Disconnected' }}
              </span>
            </div>
          </div>
        </header>

        <!-- Main Content -->
        <main class="flex-1 overflow-y-auto p-6">
          <!-- Connection Error Banner -->
          <div
            v-if="showConnectionError"
            class="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <i class="fas fa-exclamation-circle" />
                <div>
                  <h3 class="font-semibold">
                    Connection Error
                  </h3>
                  <p class="text-sm">
                    Unable to connect to the API server. Please ensure the server is running.
                  </p>
                </div>
              </div>
              <button
                class="btn btn-sm btn-danger"
                @click="testConnection"
              >
                <i class="fas fa-sync-alt mr-2" />
                Retry
              </button>
            </div>
          </div>

          <!-- Router View -->
          <router-view />
        </main>
      </div>
    </div>

    <!-- Mobile Drawer Overlay -->
    <div
      v-if="drawerOpen"
      class="fixed inset-0 z-40 lg:hidden"
    >
      <!-- Backdrop -->
      <div
        class="fixed inset-0 bg-black/50 transition-opacity"
        @click="drawerOpen = false"
      />

      <!-- Drawer -->
      <div class="fixed inset-y-0 left-0 z-50">
        <Navigation />
      </div>
    </div>

    <!-- Toast Notifications -->
    <div class="fixed bottom-4 right-4 z-50 space-y-2">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="[
          'max-w-sm px-4 py-3 rounded-lg shadow-lg animate-slide-up',
          getNotificationClass(notification.type)
        ]"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <i :class="getNotificationIcon(notification.type)" />
            <div>
              <h4 class="font-semibold">
                {{ notification.title }}
              </h4>
              <p
                v-if="notification.message"
                class="text-sm opacity-90"
              >
                {{ notification.message }}
              </p>
            </div>
          </div>
          <button
            class="ml-4 opacity-70 hover:opacity-100"
            @click="dismissNotification(notification.id)"
          >
            <i class="fas fa-times" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth.js'
import { healthApi } from './services/api.js'
import Navigation from './components/Navigation.vue'

const authStore = useAuthStore()

// State
const drawerOpen = ref(false)
const isConnected = ref(true)
const showConnectionError = ref(false)
const notifications = ref([])

// Methods
const testConnection = async () => {
  try {
    await healthApi.check()
    isConnected.value = true
    showConnectionError.value = false
    showNotification('success', 'Connected', 'Successfully connected to server')
  } catch (error) {
    isConnected.value = false
    showConnectionError.value = true
  }
}

const showNotification = (type, title, message = null) => {
  const id = Date.now()
  notifications.value.push({ id, type, title, message })

  setTimeout(() => {
    dismissNotification(id)
  }, 5000)
}

const dismissNotification = (id) => {
  notifications.value = notifications.value.filter(n => n.id !== id)
}

const getNotificationClass = (type) => {
  switch (type) {
    case 'success': return 'bg-green-600 text-white'
    case 'error': return 'bg-red-600 text-white'
    case 'warning': return 'bg-yellow-500 text-white'
    default: return 'bg-surface-700 text-white'
  }
}

const getNotificationIcon = (type) => {
  switch (type) {
    case 'success': return 'fas fa-check-circle'
    case 'error': return 'fas fa-exclamation-circle'
    case 'warning': return 'fas fa-exclamation-triangle'
    default: return 'fas fa-info-circle'
  }
}

// Lifecycle
onMounted(async () => {
  await testConnection()

  if (authStore.token) {
    await authStore.getCurrentUser()
  }
})

// Expose notification method globally
window.showNotification = showNotification
</script>

<style scoped>
#app {
  font-family: 'Inter', system-ui, sans-serif;
}
</style>
