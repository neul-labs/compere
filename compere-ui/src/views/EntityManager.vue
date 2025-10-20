<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between">
      <div>
        <h1 class="h1 font-bold text-surface-900-50-token">Entity Management</h1>
        <p class="text-surface-600-300-token text-lg">
          Manage your entities and monitor their ratings
        </p>
      </div>

      <button
        @click="showCreateModal = true"
        class="btn variant-filled-primary mt-4 lg:mt-0"
      >
        <i class="fas fa-plus"></i>
        <span class="ml-2">Add Entity</span>
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="card p-6">
      <div class="flex flex-col lg:flex-row lg:items-center space-y-4 lg:space-y-0 lg:space-x-4">
        <div class="flex-1">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search entities..."
              class="input pl-10"
            >
            <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-surface-500-400-token"></i>
          </div>
        </div>

        <div class="flex items-center space-x-4">
          <select v-model="sortBy" class="select">
            <option value="rating">Sort by Rating</option>
            <option value="name">Sort by Name</option>
            <option value="created">Sort by Created</option>
          </select>

          <button
            @click="sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'"
            class="btn variant-ghost-surface"
            :title="sortOrder === 'asc' ? 'Sort Descending' : 'Sort Ascending'"
          >
            <i :class="['fas', sortOrder === 'asc' ? 'fa-sort-up' : 'fa-sort-down']"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Entities Grid -->
    <div v-if="filteredEntities.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="entity in paginatedEntities"
        :key="entity.id"
        class="card p-6 hover-lift"
      >
        <!-- Entity Image -->
        <div class="relative mb-4">
          <div class="w-full h-48 bg-surface-200-700-token rounded-lg overflow-hidden">
            <img
              v-if="entity.image_urls && entity.image_urls[0]"
              :src="entity.image_urls[0]"
              :alt="entity.name"
              class="w-full h-full object-cover"
            >
            <div
              v-else
              class="w-full h-full flex items-center justify-center text-surface-500-400-token"
            >
              <i class="fas fa-image text-4xl"></i>
            </div>
          </div>

          <!-- Rating Badge -->
          <div class="absolute top-3 right-3">
            <div
              :class="[
                'px-3 py-1 rounded-full text-sm font-bold text-white shadow-lg',
                getRatingBadgeColor(entity.rating)
              ]"
            >
              {{ formatRating(entity.rating) }}
            </div>
          </div>
        </div>

        <!-- Entity Details -->
        <div class="space-y-3">
          <div>
            <h3 class="text-xl font-bold text-surface-900-50-token">
              {{ entity.name }}
            </h3>
            <p class="text-surface-600-300-token text-sm line-clamp-2">
              {{ entity.description }}
            </p>
          </div>

          <!-- Stats -->
          <div class="flex items-center justify-between text-sm">
            <div class="flex items-center space-x-2 text-surface-500-400-token">
              <i class="fas fa-star"></i>
              <span>{{ formatRating(entity.rating) }}</span>
            </div>
            <div class="text-surface-500-400-token">
              ID: {{ entity.id }}
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center space-x-2 pt-3">
            <button
              @click="editEntity(entity)"
              class="btn variant-ghost-surface btn-sm flex-1"
            >
              <i class="fas fa-edit"></i>
              <span class="ml-2">Edit</span>
            </button>

            <button
              @click="confirmDelete(entity)"
              class="btn variant-ghost-error btn-sm flex-1"
            >
              <i class="fas fa-trash"></i>
              <span class="ml-2">Delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-16">
      <i class="fas fa-database text-6xl text-surface-400-500-token mb-6"></i>
      <h2 class="h2 font-bold mb-4">No Entities Found</h2>
      <p class="text-surface-600-300-token text-lg mb-8">
        {{ searchQuery ? 'No entities match your search criteria.' : 'Start by creating your first entity.' }}
      </p>
      <button
        v-if="!searchQuery"
        @click="showCreateModal = true"
        class="btn variant-filled-primary"
      >
        <i class="fas fa-plus"></i>
        <span class="ml-2">Create First Entity</span>
      </button>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-center">
      <div class="btn-group variant-ghost-surface">
        <button
          @click="currentPage = Math.max(1, currentPage - 1)"
          :disabled="currentPage === 1"
          class="btn"
        >
          <i class="fas fa-chevron-left"></i>
        </button>

        <span class="btn px-4">
          {{ currentPage }} of {{ totalPages }}
        </span>

        <button
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="btn"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div
      v-if="showCreateModal || editingEntity"
      class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      @click="closeModal"
    >
      <div
        class="card max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="h2 font-bold">
              {{ editingEntity ? 'Edit Entity' : 'Create New Entity' }}
            </h2>
            <button @click="closeModal" class="btn variant-ghost-surface btn-sm">
              <i class="fas fa-times"></i>
            </button>
          </div>

          <form @submit.prevent="submitEntity" class="space-y-6">
            <div>
              <label class="label">
                <span>Name *</span>
                <input
                  v-model="entityForm.name"
                  type="text"
                  class="input"
                  required
                  maxlength="200"
                >
              </label>
            </div>

            <div>
              <label class="label">
                <span>Description</span>
                <textarea
                  v-model="entityForm.description"
                  class="textarea"
                  rows="3"
                  maxlength="1000"
                ></textarea>
              </label>
            </div>

            <div>
              <label class="label">
                <span>Image URLs (one per line)</span>
                <textarea
                  v-model="imageUrlsText"
                  class="textarea"
                  rows="4"
                  placeholder="https://example.com/image1.jpg&#10;https://example.com/image2.jpg"
                ></textarea>
              </label>
            </div>

            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="closeModal"
                class="btn variant-ghost-surface"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="submitting"
                class="btn variant-filled-primary"
              >
                <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
                <i v-else class="fas fa-save"></i>
                <span class="ml-2">{{ editingEntity ? 'Update' : 'Create' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="entityToDelete"
      class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
    >
      <div class="card max-w-md w-full">
        <div class="p-6">
          <div class="text-center">
            <i class="fas fa-exclamation-triangle text-6xl text-error-500 mb-4"></i>
            <h3 class="h3 font-bold mb-2">Delete Entity</h3>
            <p class="text-surface-600-300-token mb-6">
              Are you sure you want to delete "{{ entityToDelete.name }}"?
              This action cannot be undone.
            </p>

            <div class="flex justify-center space-x-3">
              <button
                @click="entityToDelete = null"
                class="btn variant-ghost-surface"
              >
                Cancel
              </button>
              <button
                @click="deleteEntity"
                :disabled="submitting"
                class="btn variant-filled-error"
              >
                <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
                <i v-else class="fas fa-trash"></i>
                <span class="ml-2">Delete</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useEntitiesStore } from '../stores/entities.js'
import { formatRating } from '../utils/simulation.js'

const entitiesStore = useEntitiesStore()

// State
const searchQuery = ref('')
const sortBy = ref('rating')
const sortOrder = ref('desc')
const currentPage = ref(1)
const itemsPerPage = ref(12)
const showCreateModal = ref(false)
const editingEntity = ref(null)
const entityToDelete = ref(null)
const submitting = ref(false)

// Form state
const entityForm = ref({
  name: '',
  description: '',
  image_urls: []
})
const imageUrlsText = ref('')

// Computed
const filteredEntities = computed(() => {
  let entities = [...entitiesStore.entities]

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    entities = entities.filter(entity =>
      entity.name.toLowerCase().includes(query) ||
      entity.description.toLowerCase().includes(query)
    )
  }

  // Sort
  entities.sort((a, b) => {
    let comparison = 0
    switch (sortBy.value) {
      case 'name':
        comparison = a.name.localeCompare(b.name)
        break
      case 'rating':
        comparison = a.rating - b.rating
        break
      case 'created':
        comparison = new Date(a.created_at || 0) - new Date(b.created_at || 0)
        break
    }
    return sortOrder.value === 'asc' ? comparison : -comparison
  })

  return entities
})

const paginatedEntities = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredEntities.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredEntities.value.length / itemsPerPage.value)
})

// Methods
const getRatingBadgeColor = (rating) => {
  if (rating >= 1600) return 'bg-green-500'
  if (rating >= 1500) return 'bg-yellow-500'
  if (rating >= 1400) return 'bg-orange-500'
  return 'bg-red-500'
}

const editEntity = (entity) => {
  editingEntity.value = entity
  entityForm.value = {
    name: entity.name,
    description: entity.description,
    image_urls: [...entity.image_urls]
  }
  imageUrlsText.value = entity.image_urls.join('\n')
}

const confirmDelete = (entity) => {
  entityToDelete.value = entity
}

const closeModal = () => {
  showCreateModal.value = false
  editingEntity.value = null
  entityForm.value = { name: '', description: '', image_urls: [] }
  imageUrlsText.value = ''
}

const submitEntity = async () => {
  submitting.value = true

  try {
    // Parse image URLs
    entityForm.value.image_urls = imageUrlsText.value
      .split('\n')
      .map(url => url.trim())
      .filter(url => url)

    let result
    if (editingEntity.value) {
      result = await entitiesStore.updateEntity(editingEntity.value.id, entityForm.value)
    } else {
      result = await entitiesStore.createEntity(entityForm.value)
    }

    if (result.success) {
      window.showNotification?.(
        'success',
        editingEntity.value ? 'Entity Updated' : 'Entity Created',
        `${entityForm.value.name} has been saved successfully`
      )
      closeModal()
    } else {
      window.showNotification?.('error', 'Save Failed', result.error)
    }
  } catch (error) {
    window.showNotification?.('error', 'Save Failed', error.message)
  } finally {
    submitting.value = false
  }
}

const deleteEntity = async () => {
  if (!entityToDelete.value) return

  submitting.value = true

  try {
    const result = await entitiesStore.deleteEntity(entityToDelete.value.id)

    if (result.success) {
      window.showNotification?.(
        'success',
        'Entity Deleted',
        `${entityToDelete.value.name} has been deleted`
      )
      entityToDelete.value = null
    } else {
      window.showNotification?.('error', 'Delete Failed', result.error)
    }
  } catch (error) {
    window.showNotification?.('error', 'Delete Failed', error.message)
  } finally {
    submitting.value = false
  }
}

// Watchers
watch(searchQuery, () => {
  currentPage.value = 1
})

// Lifecycle
onMounted(async () => {
  await entitiesStore.refreshEntities()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>