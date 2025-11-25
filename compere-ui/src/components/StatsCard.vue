<template>
  <div class="card p-6 hover-lift">
    <!-- Loading State -->
    <div v-if="loading" class="animate-pulse">
      <div class="flex items-center space-x-4">
        <div class="w-12 h-12 bg-surface-300 rounded-full"></div>
        <div class="space-y-2 flex-1">
          <div class="h-4 bg-surface-300 rounded w-24"></div>
          <div class="h-6 bg-surface-300 rounded w-16"></div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="flex items-center space-x-4">
      <!-- Icon -->
      <div
        :class="[
          'w-12 h-12 rounded-full flex items-center justify-center text-white text-lg',
          getColorClass(color)
        ]"
      >
        <i :class="icon"></i>
      </div>

      <!-- Stats -->
      <div class="flex-1">
        <p class="text-surface-500 font-medium">{{ title }}</p>
        <p class="text-2xl font-bold text-surface-900">
          {{ formatValue(value) }}
        </p>

        <!-- Change Indicator (if provided) -->
        <div v-if="change !== undefined" class="flex items-center space-x-1 mt-1">
          <i
            :class="[
              'fas text-xs',
              change >= 0 ? 'fa-arrow-up text-green-500' : 'fa-arrow-down text-red-500'
            ]"
          ></i>
          <span
            :class="[
              'text-xs font-medium',
              change >= 0 ? 'text-green-600' : 'text-red-600'
            ]"
          >
            {{ Math.abs(change) }}%
          </span>
          <span class="text-xs text-surface-400">from last week</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'success', 'warning', 'error', 'purple', 'green', 'yellow'].includes(value)
  },
  change: {
    type: Number,
    default: undefined
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const getColorClass = (color) => {
  const colorMap = {
    primary: 'bg-primary-500',
    secondary: 'bg-surface-500',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
    purple: 'bg-purple-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500'
  }
  return colorMap[color] || 'bg-primary-500'
}

const formatValue = (value) => {
  if (typeof value === 'number') {
    return value.toLocaleString()
  }
  return value
}
</script>
