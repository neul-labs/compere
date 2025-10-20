# Compere UI - Vue.js Simulation Interface

A modern web interface for the Compere comparative rating system, built with Vue.js, Skeleton UI, and Tailwind CSS. This application provides an interactive demonstration of how the Compere API works for various use cases.

![Compere UI Dashboard](https://via.placeholder.com/800x400/1e293b/ffffff?text=Compere+Dashboard)

## ✨ Features

### 🎮 Interactive Simulations
- **Restaurant Rankings** - Compare dining experiences and food quality
- **Pro Gamer Rankings** - Rate esports players by skill and achievements
- **Movie Ratings** - Build the ultimate movie recommendation system
- **Product Comparisons** - Compare tech products for best value

### 🧠 Smart Algorithm Visualization
- **Multi-Armed Bandit (MAB)** - Watch intelligent entity pairing in action
- **Elo Rating System** - Real-time rating updates with visual feedback
- **Comparison History** - Track every decision and rating change
- **Analytics Dashboard** - Insights into system performance

### 💫 Modern UI/UX
- **Dark/Light Mode** - Seamless theme switching
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Real-time Updates** - Live notifications and progress tracking
- **Smooth Animations** - Polished interactions and transitions

### 🔧 Complete Entity Management
- **CRUD Operations** - Create, read, update, delete entities
- **Bulk Operations** - Load simulation scenarios with one click
- **Search & Filter** - Find entities quickly with smart filtering
- **Image Support** - Rich visual entity representation

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm/yarn
- Compere API server running (see main README)

### Installation

```bash
# Navigate to UI directory
cd compere-ui

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 🎯 Usage Guide

### 1. Dashboard Overview
The main dashboard provides:
- **Quick Compare** - Start comparing entities immediately
- **System Status** - API connection and algorithm status
- **Recent Activity** - Latest comparisons and updates
- **Top Entities** - Current leaderboard preview

### 2. Entity Management
Navigate to "Entities" to:
- Add new entities with names, descriptions, and images
- Edit existing entity details
- Delete entities (with confirmation)
- Search and filter your entity collection

### 3. Interactive Comparisons
Use the "Compare" interface to:
- View MAB algorithm suggestions (when available)
- Make head-to-head comparisons
- See real-time rating updates
- Skip pairs or declare ties

### 4. Simulation Scenarios
Try pre-built scenarios in "Simulations":
- **Load Scenario** - Import entities for a specific use case
- **Quick Simulation** - Run 10 automated comparisons
- **Full Simulation** - Run 50 comparisons to see algorithm learning

### 5. Analytics & Insights
View detailed analytics including:
- Comparison history and timeline
- Rating distributions and trends
- System performance metrics
- Entity ranking changes over time

## 🎨 Customization

### Environment Configuration

Create a `.env` file:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8090

# UI Configuration
VITE_APP_TITLE=Compere - Rating System
VITE_DEFAULT_THEME=dark
```

### Theme Customization

The application uses Skeleton UI with Tailwind CSS. Customize themes in `tailwind.config.js`:

```javascript
import { skeleton } from '@skeletonlabs/tw-plugin'

export default {
  plugins: [
    skeleton({
      themes: {
        preset: [
          { name: 'wintry', enhancements: true },
          { name: 'modern', enhancements: true },
          { name: 'crimson', enhancements: true }  // Add custom themes
        ]
      }
    })
  ]
}
```

### Adding New Scenarios

Add simulation scenarios in `src/utils/simulation.js`:

```javascript
export const simulationScenarios = {
  // ... existing scenarios

  books: {
    name: 'Book Rankings',
    description: 'Compare books and authors',
    icon: '📚',
    entities: [
      {
        name: 'The Great Gatsby',
        description: 'Classic American literature',
        image_urls: ['https://example.com/gatsby.jpg'],
        category: 'Fiction'
      }
      // ... more entities
    ]
  }
}
```

## 🛠️ Development

### Project Structure

```
compere-ui/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Navigation.vue
│   │   ├── StatsCard.vue
│   │   └── ...
│   ├── views/              # Page components
│   │   ├── Dashboard.vue
│   │   ├── Comparison.vue
│   │   └── ...
│   ├── stores/             # Pinia state management
│   │   ├── auth.js
│   │   ├── entities.js
│   │   └── comparisons.js
│   ├── services/           # API clients
│   │   └── api.js
│   ├── utils/              # Helper functions
│   │   └── simulation.js
│   └── assets/             # Static assets
├── public/                 # Public assets
└── package.json
```

### Key Technologies

- **Vue 3** - Progressive JavaScript framework
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **Skeleton UI** - Component library
- **Tailwind CSS** - Utility-first CSS
- **Axios** - HTTP client
- **Vite** - Build tool and dev server

### API Integration

The application connects to the Compere API through a centralized client in `src/services/api.js`:

```javascript
// Example API call
import { entityApi } from '../services/api.js'

// Create new entity
const result = await entityApi.create({
  name: 'New Entity',
  description: 'Entity description',
  image_urls: ['https://example.com/image.jpg']
})
```

### State Management

Uses Pinia for reactive state management:

```javascript
// In a component
import { useEntitiesStore } from '../stores/entities.js'

const entitiesStore = useEntitiesStore()

// Access reactive data
const entities = computed(() => entitiesStore.sortedEntities)

// Call actions
await entitiesStore.createEntity(entityData)
```

## 🎬 Demo Use Cases

### Restaurant Rating System
Perfect for food delivery apps, review platforms, or culinary competitions. Load the restaurant scenario to see how customers might rank their favorite dining experiences.

### Esports Player Rankings
Ideal for gaming tournaments, streaming platforms, or competitive leagues. Compare professional players across different games and skill categories.

### Movie Recommendation Engine
Great for streaming services, film festivals, or entertainment apps. Build personalized movie rankings based on user preferences.

### Product Comparison Platform
Excellent for e-commerce, review sites, or consumer guides. Help customers compare tech products, features, and value propositions.

## 🔧 Troubleshooting

### Common Issues

**API Connection Failed**
- Ensure Compere API server is running on `http://localhost:8090`
- Check CORS settings if accessing from different domain
- Verify API endpoints are accessible

**Build Errors**
- Clear node_modules: `rm -rf node_modules && npm install`
- Update dependencies: `npm update`
- Check Node.js version compatibility

**Authentication Issues**
- Use demo credentials: username `admin`, password `admin123`
- Authentication is optional - you can use the app without signing in
- Clear browser storage if experiencing auth state issues

### Performance Tips

- Use browser dev tools to monitor network requests
- Enable API response caching for better performance
- Reduce image sizes for faster loading
- Use pagination for large entity lists

## 📊 Monitoring

The application includes built-in monitoring:

- **Connection Status** - Real-time API connectivity indicator
- **Request Logging** - Track API calls and performance
- **Error Handling** - User-friendly error messages and recovery
- **System Status** - Algorithm and database health checks

## 🎉 Showcase Features

### Interactive Comparisons
Experience the core Compere functionality with smooth, intuitive comparison interfaces that make choosing between entities engaging and informative.

### Algorithm Visualization
Watch the Multi-Armed Bandit algorithm learn and adapt, showing how it becomes more intelligent at suggesting meaningful comparisons over time.

### Real-time Updates
See ratings change instantly as comparisons are made, with smooth animations and clear feedback on how each decision affects the rankings.

### Comprehensive Scenarios
Explore diverse use cases from restaurants to esports, demonstrating the versatility of comparative rating systems across different domains.

---

**Ready to explore comparative ratings?** Start the Compere API server, launch this UI, and dive into intelligent entity ranking!

For questions or contributions, see the main [Compere repository](https://github.com/yourusername/compere).