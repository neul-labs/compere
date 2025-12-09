<template>
  <div class="flex items-center justify-between p-3 rounded-lg bg-surface-100">
    <div class="flex items-center space-x-3">
      <i :class="[icon, 'w-5 text-surface-500']" />
      <span class="font-medium text-surface-700">{{ label }}</span>
    </div>

    <div class="flex items-center space-x-2">
      <div
        :class="[
          'w-3 h-3 rounded-full',
          getStatusColor(status)
        ]"
      />
      <span
        :class="[
          'text-sm font-medium capitalize',
          getStatusTextColor(status)
        ]"
      >
        {{ status }}
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  status: {
    type: String,
    required: true,
    validator: (value) => ['active', 'warning', 'error', 'inactive'].includes(value)
  },
  icon: {
    type: String,
    required: true
  }
})

const getStatusColor = (status) => {
  switch (status) {
    case 'active': return 'bg-green-500'
    case 'warning': return 'bg-yellow-500'
    case 'error': return 'bg-red-500'
    case 'inactive': return 'bg-gray-500'
    default: return 'bg-gray-500'
  }
}

const getStatusTextColor = (status) => {
  switch (status) {
    case 'active': return 'text-green-600'
    case 'warning': return 'text-yellow-600'
    case 'error': return 'text-red-600'
    case 'inactive': return 'text-gray-600'
    default: return 'text-gray-600'
  }
}
</script>
