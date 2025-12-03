<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-surface-900">Entity Management</h1>
        <p class="text-surface-500">Manage your entities and monitor their ratings</p>
      </div>

      <button @click="showCreateModal = true" class="btn btn-primary">
        <i class="fas fa-plus mr-2"></i>
        Add Entity
      </button>
    </div>

    <!-- Search -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1 relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search entities..."
            class="input pl-10"
          >
          <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-surface-400"></i>
        </div>

        <select v-model="sortBy" class="input w-auto">
          <option value="rating">Sort by Rating</option>
          <option value="name">Sort by Name</option>
        </select>
      </div>
    </div>

    <!-- Entities Grid -->
    <div v-if="filteredEntities.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="entity in filteredEntities"
        :key="entity.id"
        class="card p-4 hover-lift"
      >
        <div class="aspect-video bg-surface-100 rounded-lg mb-4 overflow-hidden">
          <img
            v-if="entity.image_urls?.[0]"
            :src="entity.image_urls[0]"
            :alt="entity.name"
            class="w-full h-full object-cover"
          >
          <div v-else class="w-full h-full flex items-center justify-center">
            <i class="fas fa-image text-4xl text-surface-300"></i>
          </div>
        </div>

        <h3 class="font-bold text-surface-900">{{ entity.name }}</h3>
        <p class="text-sm text-surface-500 mt-1 line-clamp-2">{{ entity.description }}</p>

        <div class="flex items-center justify-between mt-4 pt-4 border-t border-surface-200">
          <span class="text-primary-600 font-semibold">{{ Math.round(entity.rating) }}</span>
          <div class="flex space-x-2">
            <button @click="editEntity(entity)" class="btn btn-sm btn-ghost">
              <i class="fas fa-edit"></i>
            </button>
            <button @click="confirmDelete(entity)" class="btn btn-sm btn-ghost text-red-500">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-16">
      <i class="fas fa-database text-5xl text-surface-300 mb-4"></i>
      <h2 class="text-xl font-bold text-surface-900 mb-2">No Entities Found</h2>
      <p class="text-surface-500 mb-6">
        {{ searchQuery ? 'No entities match your search.' : 'Start by creating your first entity.' }}
      </p>
      <button v-if="!searchQuery" @click="showCreateModal = true" class="btn btn-primary">
        <i class="fas fa-plus mr-2"></i>
        Create First Entity
      </button>
    </div>

    <!-- Create/Edit Modal -->
    <div
      v-if="showCreateModal || editingEntity"
      class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      @click="closeModal"
    >
      <div class="card max-w-lg w-full" @click.stop>
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-bold text-surface-900">
              {{ editingEntity ? 'Edit Entity' : 'Create New Entity' }}
            </h2>
            <button @click="closeModal" class="btn btn-sm btn-ghost">
              <i class="fas fa-times"></i>
            </button>
          </div>

          <form @submit.prevent="submitEntity" class="space-y-4">
            <div>
              <label class="label">Name *</label>
              <input v-model="entityForm.name" type="text" class="input" required maxlength="200">
            </div>

            <div>
              <label class="label">Description</label>
              <textarea v-model="entityForm.description" class="input" rows="3" maxlength="1000"></textarea>
            </div>

            <div>
              <label class="label">Image URLs (one per line)</label>
              <textarea
                v-model="imageUrlsText"
                class="input"
                rows="3"
                placeholder="https://example.com/image.jpg"
              ></textarea>
            </div>

            <div class="flex justify-end space-x-3 pt-4">
              <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" :disabled="submitting" class="btn btn-primary">
                <i v-if="submitting" class="fas fa-spinner fa-spin mr-2"></i>
                {{ editingEntity ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete Modal -->
    <div
      v-if="entityToDelete"
      class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
    >
      <div class="card max-w-sm w-full p-6 text-center">
        <i class="fas fa-exclamation-triangle text-5xl text-red-500 mb-4"></i>
        <h3 class="text-lg font-bold text-surface-900 mb-2">Delete Entity?</h3>
        <p class="text-surface-500 mb-6">
          Are you sure you want to delete "{{ entityToDelete.name }}"?
        </p>
        <div class="flex justify-center space-x-3">
          <button @click="entityToDelete = null" class="btn btn-secondary">Cancel</button>
          <button @click="deleteEntity" :disabled="submitting" class="btn btn-danger">
            <i v-if="submitting" class="fas fa-spinner fa-spin mr-2"></i>
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useEntitiesStore } from '../stores/entities.js'

const entitiesStore = useEntitiesStore()

const searchQuery = ref('')
const sortBy = ref('rating')
const showCreateModal = ref(false)
const editingEntity = ref(null)
const entityToDelete = ref(null)
const submitting = ref(false)

const entityForm = ref({ name: '', description: '', image_urls: [] })
const imageUrlsText = ref('')

const filteredEntities = computed(() => {
  let entities = [...entitiesStore.entities]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    entities = entities.filter(e =>
      e.name.toLowerCase().includes(query) ||
      e.description?.toLowerCase().includes(query)
    )
  }

  entities.sort((a, b) => {
    if (sortBy.value === 'name') return a.name.localeCompare(b.name)
    return b.rating - a.rating
  })

  return entities
})

const editEntity = (entity) => {
  editingEntity.value = entity
  entityForm.value = {
    name: entity.name,
    description: entity.description,
    image_urls: [...(entity.image_urls || [])]
  }
  imageUrlsText.value = (entity.image_urls || []).join('\n')
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
      window.showNotification?.('success', editingEntity.value ? 'Updated' : 'Created', `${entityForm.value.name} saved`)
      closeModal()
    } else {
      window.showNotification?.('error', 'Error', result.error)
    }
  } catch (error) {
    window.showNotification?.('error', 'Error', error.message)
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
      window.showNotification?.('success', 'Deleted', `${entityToDelete.value.name} deleted`)
      entityToDelete.value = null
    } else {
      window.showNotification?.('error', 'Error', result.error)
    }
  } catch (error) {
    window.showNotification?.('error', 'Error', error.message)
  } finally {
    submitting.value = false
  }
}

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
