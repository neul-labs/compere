<template>
  <div class="relative">
    <!-- User Avatar/Login Button -->
    <button
      v-if="authStore.isAuthenticated"
      :class="[
        'btn',
        showMenu ? 'btn-primary' : 'btn-ghost'
      ]"
      @click="showMenu = !showMenu"
    >
      <div class="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
        <span class="text-white text-sm font-bold">
          {{ getUserInitials() }}
        </span>
      </div>
      <span class="hidden md:inline ml-2 text-surface-700">{{ authStore.user?.username }}</span>
      <i
        class="fas fa-chevron-down ml-2 transition-transform text-surface-500"
        :class="{ 'rotate-180': showMenu }"
      />
    </button>

    <router-link
      v-else
      to="/auth"
      class="btn btn-primary"
    >
      <i class="fas fa-sign-in-alt" />
      <span class="hidden sm:inline ml-2">Login</span>
    </router-link>

    <!-- Dropdown Menu -->
    <div
      v-if="authStore.isAuthenticated && showMenu"
      class="absolute right-0 top-full mt-2 w-64 bg-white rounded-lg shadow-xl border border-surface-200 z-50 animate-slide-up"
      @click.stop
    >
      <!-- User Info -->
      <div class="p-4 border-b border-surface-200">
        <div class="flex items-center space-x-3">
          <div class="w-12 h-12 bg-primary-500 rounded-full flex items-center justify-center">
            <span class="text-white font-bold text-lg">
              {{ getUserInitials() }}
            </span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-surface-900 truncate">
              {{ authStore.user?.username }}
            </p>
            <p class="text-sm text-surface-500 truncate">
              {{ authStore.user?.email || 'Compere User' }}
            </p>
            <p class="text-xs text-surface-400">
              {{ authStore.user?.full_name || 'Active User' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Menu Items -->
      <div class="p-2">
        <button
          class="w-full text-left px-3 py-2 rounded-lg hover:bg-surface-100 transition-colors flex items-center space-x-3 text-surface-700"
          @click="viewProfile"
        >
          <i class="fas fa-user w-5" />
          <span>Profile</span>
        </button>

        <button
          class="w-full text-left px-3 py-2 rounded-lg hover:bg-surface-100 transition-colors flex items-center space-x-3 text-surface-700"
          @click="viewSettings"
        >
          <i class="fas fa-cog w-5" />
          <span>Settings</span>
        </button>

        <hr class="my-2 border-surface-200">

        <button
          class="w-full text-left px-3 py-2 rounded-lg hover:bg-surface-100 transition-colors flex items-center space-x-3 text-surface-700"
          @click="toggleTheme"
        >
          <i :class="['fas', isDark ? 'fa-sun' : 'fa-moon', 'w-5']" />
          <span>{{ isDark ? 'Light Mode' : 'Dark Mode' }}</span>
        </button>

        <hr class="my-2 border-surface-200">

        <button
          class="w-full text-left px-3 py-2 rounded-lg hover:bg-red-50 transition-colors flex items-center space-x-3 text-red-600"
          @click="logout"
        >
          <i class="fas fa-sign-out-alt w-5" />
          <span>Logout</span>
        </button>
      </div>
    </div>

    <!-- Backdrop -->
    <div
      v-if="showMenu"
      class="fixed inset-0 z-40"
      @click="showMenu = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

// State
const showMenu = ref(false)
const isDark = ref(false)

// Computed
const getUserInitials = () => {
  if (!authStore.user?.username) return '?'
  const username = authStore.user.username
  return username.charAt(0).toUpperCase()
}

// Methods
const viewProfile = () => {
  showMenu.value = false
  // Navigate to profile page when implemented
  window.showNotification?.('info', 'Profile', 'Profile page coming soon!')
}

const viewSettings = () => {
  showMenu.value = false
  // Navigate to settings page when implemented
  window.showNotification?.('info', 'Settings', 'Settings page coming soon!')
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  showMenu.value = false

  window.showNotification?.(
    'success',
    'Theme Changed',
    `Switched to ${isDark.value ? 'dark' : 'light'} mode`
  )
}

const logout = async () => {
  showMenu.value = false
  authStore.logout()
  router.push('/')

  window.showNotification?.('success', 'Logged Out', 'Successfully logged out')
}

// Initialize theme
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    isDark.value = savedTheme === 'dark'
  }
  document.documentElement.classList.toggle('dark', isDark.value)
})
</script>

<style scoped>
.animate-slide-up {
  animation: slideUp 0.2s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
