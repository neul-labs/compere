<template>
  <div id="app" class="min-h-screen bg-surface-50-900-token">
    <!-- App Shell -->
    <AppShell>
      <!-- Navigation Sidebar -->
      <svelte:fragment slot="sidebarLeft">
        <Navigation />
      </svelte:fragment>

      <!-- Header -->
      <svelte:fragment slot="header">
        <AppBar>
          <svelte:fragment slot="lead">
            <div class="flex items-center space-x-4">
              <button
                @click="drawerOpen = !drawerOpen"
                class="btn btn-sm variant-ghost-surface lg:hidden"
              >
                <i class="fas fa-bars"></i>
              </button>
              <h1 class="h3 font-bold">Compere</h1>
            </div>
          </svelte:fragment>
          <svelte:fragment slot="trail">
            <ConnectionStatus />
            <UserMenu />
          </svelte:fragment>
        </AppBar>
      </svelte:fragment>

      <!-- Main Content -->
      <div class="container mx-auto px-4 py-8 space-y-8">
        <!-- Connection Error Banner -->
        <div
          v-if="showConnectionError"
          class="alert variant-filled-error animate-slide-up"
        >
          <div class="alert-message">
            <h3 class="h4">Connection Error</h3>
            <p>Unable to connect to Compere API server. Please ensure the server is running.</p>
          </div>
          <div class="alert-actions">
            <button @click="testConnection" class="btn variant-filled">
              <i class="fas fa-sync-alt"></i>
              <span>Retry</span>
            </button>
          </div>
        </div>

        <!-- Router View -->
        <div class="animate-bounce-in">
          <router-view />
        </div>
      </div>
    </AppShell>

    <!-- Mobile Drawer -->
    <Drawer bind:open={drawerOpen} class="lg:hidden">
      <Navigation />
    </Drawer>

    <!-- Global Loading Overlay -->
    <div
      v-if="isGlobalLoading"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    >
      <div class="card p-8">
        <div class="flex flex-col items-center space-y-4">
          <ProgressRadial width="w-16" />
          <p class="font-medium">Loading...</p>
        </div>
      </div>
    </div>

    <!-- Toast Notifications -->
    <div class="fixed top-4 right-4 z-40 space-y-2">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="[
          'alert max-w-md animate-slide-up',
          getNotificationClass(notification.type)
        ]"
      >
        <div class="alert-message">
          <h4 class="font-semibold">{{ notification.title }}</h4>
          <p v-if="notification.message">{{ notification.message }}</p>
        </div>
        <div class="alert-actions">
          <button
            @click="dismissNotification(notification.id)"
            class="btn btn-sm variant-ghost"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth.js'
import { healthApi } from './services/api.js'

// Components
import Navigation from './components/Navigation.vue'
import ConnectionStatus from './components/ConnectionStatus.vue'
import UserMenu from './components/UserMenu.vue'

// Skeleton UI components (these would be imported from skeleton)
// import { AppShell, AppBar, Drawer, ProgressRadial } from '@skeletonlabs/skeleton'

const router = useRouter()
const authStore = useAuthStore()

// State
const drawerOpen = ref(false)
const isConnected = ref(true)
const showConnectionError = ref(false)
const notifications = ref([])
const globalLoading = ref(false)

// Computed
const isGlobalLoading = computed(() => globalLoading.value)

// Methods
const testConnection = async () => {
  try {
    await healthApi.check()
    isConnected.value = true
    showConnectionError.value = false
    showNotification('success', 'Connected', 'Successfully connected to Compere server')
  } catch (error) {
    isConnected.value = false
    showConnectionError.value = true
  }
}

const showNotification = (type, title, message = null) => {
  const id = Date.now()
  notifications.value.push({ id, type, title, message })

  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    dismissNotification(id)
  }, 5000)
}

const dismissNotification = (id) => {
  notifications.value = notifications.value.filter(n => n.id !== id)
}

const getNotificationClass = (type) => {
  switch (type) {
    case 'success': return 'variant-filled-success'
    case 'error': return 'variant-filled-error'
    case 'warning': return 'variant-filled-warning'
    default: return 'variant-filled-surface'
  }
}

// Lifecycle
onMounted(async () => {
  await testConnection()

  // Check auth status if token exists
  if (authStore.token) {
    await authStore.getCurrentUser()
  }
})

// Expose notification method globally
window.showNotification = showNotification
</script>

<style scoped>
/* Component-specific styles */
#app {
  font-family: 'Inter', sans-serif;
}

.alert {
  @apply shadow-lg border;
}

.animate-slide-up {
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>