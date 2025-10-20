<template>
  <nav class="h-full p-4 space-y-2 bg-surface-100-800-token">
    <!-- Logo -->
    <div class="flex items-center space-x-3 pb-4 border-b border-surface-300-600-token">
      <div class="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
        <i class="fas fa-chart-line text-white text-lg"></i>
      </div>
      <div>
        <h2 class="h4 font-bold">Compere</h2>
        <p class="text-xs text-surface-600-300-token">Rating System</p>
      </div>
    </div>

    <!-- Navigation Items -->
    <div class="space-y-1">
      <NavigationItem
        to="/"
        icon="fas fa-home"
        label="Dashboard"
        :isActive="$route.name === 'Dashboard'"
      />

      <NavigationItem
        to="/entities"
        icon="fas fa-database"
        label="Entities"
        :isActive="$route.name === 'EntityManager'"
      />

      <NavigationItem
        to="/compare"
        icon="fas fa-balance-scale"
        label="Compare"
        :isActive="$route.name === 'Comparison'"
      />

      <NavigationItem
        to="/leaderboard"
        icon="fas fa-trophy"
        label="Leaderboard"
        :isActive="$route.name === 'Leaderboard'"
      />

      <NavigationItem
        to="/analytics"
        icon="fas fa-chart-bar"
        label="Analytics"
        :isActive="$route.name === 'Analytics'"
      />

      <NavigationItem
        to="/simulations"
        icon="fas fa-play-circle"
        label="Simulations"
        :isActive="$route.name === 'Simulations'"
      />

      <!-- Separator -->
      <hr class="!my-4 opacity-20">

      <!-- Authentication -->
      <NavigationItem
        v-if="!authStore.isAuthenticated"
        to="/auth"
        icon="fas fa-sign-in-alt"
        label="Login"
        :isActive="$route.name === 'Auth'"
      />

      <button
        v-else
        @click="authStore.logout"
        class="w-full text-left px-3 py-2 rounded-lg hover:bg-surface-200-700-token transition-colors flex items-center space-x-3 text-error-500"
      >
        <i class="fas fa-sign-out-alt w-5"></i>
        <span class="font-medium">Logout</span>
      </button>
    </div>

    <!-- User Info (if authenticated) -->
    <div
      v-if="authStore.user"
      class="mt-auto pt-4 border-t border-surface-300-600-token"
    >
      <div class="flex items-center space-x-3 p-3 rounded-lg bg-surface-200-700-token">
        <div class="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
          <span class="text-white text-sm font-bold">
            {{ getUserInitials(authStore.user.username) }}
          </span>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium truncate">{{ authStore.user.username }}</p>
          <p class="text-xs text-surface-600-300-token truncate">
            {{ authStore.user.email || 'User' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Version Info -->
    <div class="mt-auto pt-4">
      <div class="text-xs text-surface-500-400-token text-center">
        <p>Compere UI v0.1.0</p>
        <p>Built with Vue.js & Skeleton</p>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import NavigationItem from './NavigationItem.vue'

const authStore = useAuthStore()

const getUserInitials = (username) => {
  if (!username) return '?'
  return username.charAt(0).toUpperCase()
}
</script>

<style scoped>
nav {
  width: 280px;
  min-height: 100vh;
}

@media (max-width: 1024px) {
  nav {
    width: 240px;
  }
}
</style>