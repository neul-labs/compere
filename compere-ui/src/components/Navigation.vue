<template>
  <nav class="w-64 h-screen bg-surface-900 text-white p-4 flex flex-col sticky top-0 overflow-hidden">
    <!-- Logo -->
    <div class="flex items-center space-x-3 pb-6 border-b border-surface-700">
      <div class="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
        <i class="fas fa-chart-line text-white text-lg"></i>
      </div>
      <div>
        <h2 class="text-lg font-bold">Compere</h2>
        <p class="text-xs text-surface-400">Rating System</p>
      </div>
    </div>

    <!-- Navigation Items -->
    <div class="flex-1 py-6 space-y-1">
      <router-link
        to="/"
        class="nav-item"
        :class="{ 'nav-item-active': $route.path === '/' }"
      >
        <i class="fas fa-home w-5"></i>
        <span>Dashboard</span>
      </router-link>

      <router-link
        to="/entities"
        class="nav-item"
        :class="{ 'nav-item-active': $route.path === '/entities' }"
      >
        <i class="fas fa-database w-5"></i>
        <span>Entities</span>
      </router-link>

      <router-link
        to="/compare"
        class="nav-item"
        :class="{ 'nav-item-active': $route.path === '/compare' }"
      >
        <i class="fas fa-balance-scale w-5"></i>
        <span>Compare</span>
      </router-link>

      <router-link
        to="/leaderboard"
        class="nav-item"
        :class="{ 'nav-item-active': $route.path === '/leaderboard' }"
      >
        <i class="fas fa-trophy w-5"></i>
        <span>Leaderboard</span>
      </router-link>

      <router-link
        to="/analytics"
        class="nav-item"
        :class="{ 'nav-item-active': $route.path === '/analytics' }"
      >
        <i class="fas fa-chart-bar w-5"></i>
        <span>Analytics</span>
      </router-link>

      <router-link
        to="/simulations"
        class="nav-item"
        :class="{ 'nav-item-active': $route.path === '/simulations' }"
      >
        <i class="fas fa-play-circle w-5"></i>
        <span>Simulations</span>
      </router-link>
    </div>

    <!-- Footer -->
    <div class="pt-4 border-t border-surface-700">
      <div class="text-xs text-surface-500 text-center">
        <p>Compere v0.1.0</p>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../stores/auth.js'

const authStore = useAuthStore()
</script>

<style scoped>
.nav-item {
  @apply flex items-center space-x-3 px-3 py-2.5 rounded-lg text-surface-300 hover:bg-surface-800 hover:text-white transition-colors;
}

.nav-item-active {
  @apply bg-primary-600 text-white hover:bg-primary-600;
}
</style>
