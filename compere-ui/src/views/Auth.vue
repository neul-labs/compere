<template>
  <div class="min-h-[60vh] flex items-center justify-center">
    <div class="card p-8 max-w-md w-full">
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-primary-500 rounded-full mx-auto mb-4 flex items-center justify-center">
          <i class="fas fa-sign-in-alt text-white text-2xl" />
        </div>
        <h1 class="text-xl font-bold text-surface-900 mb-2">
          Welcome to Compere
        </h1>
        <p class="text-surface-500">
          Sign in to access your rating system
        </p>
      </div>

      <form
        class="space-y-6"
        @submit.prevent="login"
      >
        <div>
          <label class="label">
            <span class="text-surface-700 font-medium">Username</span>
            <input
              v-model="credentials.username"
              type="text"
              class="input mt-1"
              required
              placeholder="Enter your username"
            >
          </label>
        </div>

        <div>
          <label class="label">
            <span class="text-surface-700 font-medium">Password</span>
            <input
              v-model="credentials.password"
              type="password"
              class="input mt-1"
              required
              placeholder="Enter your password"
            >
          </label>
        </div>

        <button
          type="submit"
          :disabled="authStore.isLoading"
          class="w-full btn btn-primary"
        >
          <i
            v-if="authStore.isLoading"
            class="fas fa-spinner fa-spin"
          />
          <i
            v-else
            class="fas fa-sign-in-alt"
          />
          <span class="ml-2">{{ authStore.isLoading ? 'Signing In...' : 'Sign In' }}</span>
        </button>

        <div
          v-if="authStore.error"
          class="p-4 rounded-lg bg-red-100 border border-red-300 text-red-700"
        >
          <div class="flex items-center space-x-2">
            <i class="fas fa-exclamation-triangle" />
            <span>{{ authStore.error }}</span>
          </div>
        </div>
      </form>

      <!-- Demo Credentials -->
      <div class="mt-8 p-4 rounded-lg bg-surface-100">
        <h3 class="font-semibold text-surface-900 mb-3">
          Demo Credentials:
        </h3>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-surface-600">Username:</span>
            <code class="bg-surface-200 px-2 py-1 rounded text-surface-800">admin</code>
          </div>
          <div class="flex justify-between">
            <span class="text-surface-600">Password:</span>
            <code class="bg-surface-200 px-2 py-1 rounded text-surface-800">admin123</code>
          </div>
        </div>
        <button
          class="mt-3 btn btn-secondary btn-sm w-full"
          @click="fillDemo"
        >
          Use Demo Credentials
        </button>
      </div>

      <div class="mt-6 text-center text-sm text-surface-500">
        <p>Authentication is optional. You can use Compere without signing in.</p>
        <router-link
          to="/"
          class="text-primary-600 hover:underline"
        >
          Continue without authentication
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const credentials = ref({
  username: '',
  password: ''
})

const login = async () => {
  const result = await authStore.login(credentials.value.username, credentials.value.password)

  if (result.success) {
    window.showNotification?.('success', 'Welcome!', `Signed in as ${credentials.value.username}`)
    router.push('/')
  }
}

const fillDemo = () => {
  credentials.value = {
    username: 'admin',
    password: 'admin123'
  }
}

onMounted(() => {
  // Clear any previous errors
  authStore.clearError()

  // Redirect if already authenticated
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})
</script>
