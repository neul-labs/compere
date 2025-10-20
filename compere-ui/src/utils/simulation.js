// Simulation data and helpers

export const simulationScenarios = {
  restaurants: {
    name: 'Restaurant Rankings',
    description: 'Compare restaurants to find the best dining experiences',
    icon: '🍴',
    entities: [
      {
        name: 'The Golden Fork',
        description: 'Upscale fine dining with seasonal menus and exceptional service',
        image_urls: ['https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400'],
        category: 'Fine Dining'
      },
      {
        name: 'Mario\'s Pizzeria',
        description: 'Authentic wood-fired pizza with family recipes from Italy',
        image_urls: ['https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400'],
        category: 'Italian'
      },
      {
        name: 'Sakura Sushi',
        description: 'Fresh sushi and sashimi prepared by master chefs',
        image_urls: ['https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=400'],
        category: 'Japanese'
      },
      {
        name: 'Burger Junction',
        description: 'Gourmet burgers with locally sourced ingredients',
        image_urls: ['https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400'],
        category: 'American'
      },
      {
        name: 'Spice Garden',
        description: 'Authentic Indian cuisine with traditional spices and flavors',
        image_urls: ['https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400'],
        category: 'Indian'
      },
      {
        name: 'Le Petit Café',
        description: 'Cozy French bistro with classic dishes and fine wines',
        image_urls: ['https://images.unsplash.com/photo-1551218808-94e220e084d2?w=400'],
        category: 'French'
      }
    ]
  },

  gamers: {
    name: 'Pro Gamer Rankings',
    description: 'Rank professional esports players by skill and achievements',
    icon: '🎮',
    entities: [
      {
        name: 'Alex "Lightning" Chen',
        description: 'Professional FPS player with multiple championship wins',
        image_urls: ['https://images.unsplash.com/photo-1511512578047-dfb367046420?w=400'],
        category: 'FPS'
      },
      {
        name: 'Sarah "Phoenix" Rodriguez',
        description: 'MOBA specialist known for strategic gameplay and leadership',
        image_urls: ['https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400'],
        category: 'MOBA'
      },
      {
        name: 'Kim "Ninja" Park',
        description: 'Versatile streamer and competitive player across multiple games',
        image_urls: ['https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=400'],
        category: 'Multi-game'
      },
      {
        name: 'Marcus "Tank" Johnson',
        description: 'Fighting game champion with unmatched combo execution',
        image_urls: ['https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400'],
        category: 'Fighting'
      },
      {
        name: 'Emma "Strategist" Walsh',
        description: 'RTS player known for innovative tactics and micro management',
        image_urls: ['https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400'],
        category: 'RTS'
      }
    ]
  },

  movies: {
    name: 'Movie Rankings',
    description: 'Compare and rank movies to find the ultimate favorites',
    icon: '🎬',
    entities: [
      {
        name: 'The Shawshank Redemption',
        description: 'Drama about hope and friendship in prison, directed by Frank Darabont',
        image_urls: ['https://images.unsplash.com/photo-1489599184108-1b07ea82f08f?w=400'],
        category: 'Drama'
      },
      {
        name: 'Inception',
        description: 'Mind-bending sci-fi thriller about dreams within dreams',
        image_urls: ['https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=400'],
        category: 'Sci-Fi'
      },
      {
        name: 'Pulp Fiction',
        description: 'Quentin Tarantino\'s nonlinear crime masterpiece',
        image_urls: ['https://images.unsplash.com/photo-1489599184108-1b07ea82f08f?w=400'],
        category: 'Crime'
      },
      {
        name: 'The Dark Knight',
        description: 'Batman faces the Joker in this acclaimed superhero film',
        image_urls: ['https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400'],
        category: 'Action'
      },
      {
        name: 'Spirited Away',
        description: 'Studio Ghibli\'s magical animated adventure',
        image_urls: ['https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400'],
        category: 'Animation'
      }
    ]
  },

  products: {
    name: 'Product Comparison',
    description: 'Compare tech products to find the best value and features',
    icon: '📱',
    entities: [
      {
        name: 'iPhone 15 Pro',
        description: 'Apple\'s flagship smartphone with advanced camera system',
        image_urls: ['https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400'],
        category: 'Smartphone'
      },
      {
        name: 'Samsung Galaxy S24',
        description: 'Android flagship with AI features and excellent display',
        image_urls: ['https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400'],
        category: 'Smartphone'
      },
      {
        name: 'MacBook Pro M3',
        description: 'High-performance laptop for creative professionals',
        image_urls: ['https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400'],
        category: 'Laptop'
      },
      {
        name: 'Dell XPS 13',
        description: 'Premium Windows laptop with excellent build quality',
        image_urls: ['https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400'],
        category: 'Laptop'
      },
      {
        name: 'Sony WH-1000XM5',
        description: 'Premium noise-canceling headphones with superior sound',
        image_urls: ['https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'],
        category: 'Audio'
      }
    ]
  }
}

export const generateRandomComparisons = (entities, count = 10) => {
  const comparisons = []

  for (let i = 0; i < count && entities.length >= 2; i++) {
    const entity1 = entities[Math.floor(Math.random() * entities.length)]
    let entity2 = entities[Math.floor(Math.random() * entities.length)]

    // Ensure different entities
    while (entity2.id === entity1.id && entities.length > 1) {
      entity2 = entities[Math.floor(Math.random() * entities.length)]
    }

    // Random winner (with slight bias toward higher rated if they exist)
    const winner = Math.random() > 0.5 ? entity1 : entity2

    comparisons.push({
      entity1_id: entity1.id,
      entity2_id: entity2.id,
      selected_entity_id: winner.id,
      timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000) // Random time in last 30 days
    })
  }

  return comparisons
}

export const simulateComparisons = async (entityStore, comparisonStore, scenario, count = 20) => {
  const results = {
    created: 0,
    errors: [],
    duration: 0
  }

  const startTime = Date.now()

  try {
    // Create entities first
    const createdEntities = []
    for (const entityData of scenario.entities) {
      const result = await entityStore.createEntity(entityData)
      if (result.success) {
        createdEntities.push(result.data)
      } else {
        results.errors.push(`Failed to create ${entityData.name}: ${result.error}`)
      }
    }

    if (createdEntities.length < 2) {
      throw new Error('Need at least 2 entities for comparisons')
    }

    // Generate and create comparisons
    const comparisons = generateRandomComparisons(createdEntities, count)

    for (const comparison of comparisons) {
      const result = await comparisonStore.createComparison(comparison)
      if (result.success) {
        results.created++
      } else {
        results.errors.push(`Failed to create comparison: ${result.error}`)
      }

      // Small delay to avoid overwhelming the API
      await new Promise(resolve => setTimeout(resolve, 100))
    }

  } catch (error) {
    results.errors.push(error.message)
  }

  results.duration = Date.now() - startTime
  return results
}

export const formatRating = (rating) => {
  return Math.round(rating).toLocaleString()
}

export const getRatingColor = (rating) => {
  if (rating >= 1600) return 'text-green-500'
  if (rating >= 1500) return 'text-yellow-500'
  if (rating >= 1400) return 'text-orange-500'
  return 'text-red-500'
}

export const getRatingBadge = (rating) => {
  if (rating >= 1700) return { text: 'Elite', class: 'badge-gold' }
  if (rating >= 1600) return { text: 'Expert', class: 'badge-silver' }
  if (rating >= 1500) return { text: 'Advanced', class: 'badge-bronze' }
  if (rating >= 1400) return { text: 'Intermediate', class: 'badge-blue' }
  return { text: 'Beginner', class: 'badge-gray' }
}