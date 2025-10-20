import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from './views/Dashboard.vue'
import EntityManager from './views/EntityManager.vue'
import Comparison from './views/Comparison.vue'
import Leaderboard from './views/Leaderboard.vue'
import Analytics from './views/Analytics.vue'
import Simulations from './views/Simulations.vue'
import Auth from './views/Auth.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: 'Dashboard'
    }
  },
  {
    path: '/entities',
    name: 'EntityManager',
    component: EntityManager,
    meta: {
      title: 'Entity Manager'
    }
  },
  {
    path: '/compare',
    name: 'Comparison',
    component: Comparison,
    meta: {
      title: 'Compare Entities'
    }
  },
  {
    path: '/leaderboard',
    name: 'Leaderboard',
    component: Leaderboard,
    meta: {
      title: 'Leaderboard & Rankings'
    }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: Analytics,
    meta: {
      title: 'Analytics & History'
    }
  },
  {
    path: '/simulations',
    name: 'Simulations',
    component: Simulations,
    meta: {
      title: 'Simulation Scenarios'
    }
  },
  {
    path: '/auth',
    name: 'Auth',
    component: Auth,
    meta: {
      title: 'Authentication'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Update document title
router.afterEach((to) => {
  document.title = `${to.meta.title} - Compere`
})

export default router