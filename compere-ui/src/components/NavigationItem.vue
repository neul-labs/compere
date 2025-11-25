<template>
  <router-link
    :to="to"
    :class="[
      'flex items-center space-x-3 px-3 py-2 rounded-lg font-medium transition-all duration-200',
      isActive
        ? 'bg-primary-500 text-white shadow-md'
        : 'text-surface-700 hover:bg-surface-200 hover:text-primary-600'
    ]"
    @click="$emit('navigate')"
  >
    <i :class="[icon, 'w-5 text-center']"></i>
    <span>{{ label }}</span>

    <!-- Active indicator -->
    <div
      v-if="isActive"
      class="w-2 h-2 bg-white rounded-full ml-auto opacity-80"
    ></div>
  </router-link>
</template>

<script setup>
defineProps({
  to: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: true
  },
  isActive: {
    type: Boolean,
    default: false
  }
})

defineEmits(['navigate'])
</script>
