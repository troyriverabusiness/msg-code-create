# Client Application

A modern Vue.js 3 frontend application for the train travel planning system, featuring an AI-powered conversational interface and comprehensive journey planning capabilities.

## Architecture Overview

The client is built as a **Single Page Application (SPA)** using Vue.js 3 with a component-based architecture. It communicates with a FastAPI backend server through RESTful API endpoints, providing a seamless user experience for planning train journeys in Germany.

### Technology Stack

- **Framework**: Vue.js 3 (Composition API)
- **UI Library**: Vuetify 3 (Material Design components)
- **State Management**: Pinia
- **Routing**: Vue Router 4
- **HTTP Client**: Axios
- **Build Tool**: Vite 7
- **Styling**: SCSS with Vuetify theming

### Key Features

- 🤖 **AI-Powered Chat Interface**: Natural language travel planning with conversational AI
- 🔍 **Station Search**: Real-time autocomplete station search with debouncing
- 🚂 **Journey Planning**: Comprehensive connection search with via stations and transfer times
- 📱 **Responsive Design**: Mobile-first design with Vuetify components
- 🎨 **Modern UI**: Deutsche Bahn-inspired design with custom styling
- 💾 **Session Management**: Persistent chat sessions using localStorage

## Project Structure

```
client/
├── src/
│   ├── assets/          # Images and static assets
│   ├── components/      # Reusable Vue components
│   │   ├── CoachSequence.vue    # Train coach/wagon visualization
│   │   ├── DateTimePicker.vue   # Date and time selection component
│   │   ├── NavBar.vue           # Navigation bar component
│   │   └── SeatSelection.vue    # Seat selection interface
│   ├── pages/          # Route pages (auto-routed by vue-router)
│   │   ├── index.vue           # Home page with chat and search
│   │   ├── connections.vue     # Journey results display
│   │   └── login.vue            # Authentication (if needed)
│   ├── plugins/        # Vue plugins configuration
│   │   ├── index.js            # Plugin registration
│   │   └── vuetify.js          # Vuetify configuration
│   ├── router/         # Vue Router configuration
│   │   └── index.js           # Auto-routing setup
│   ├── stores/         # Pinia state stores
│   │   └── backendCalls.js    # API calls and state management
│   ├── styles/         # Global styles
│   │   └── settings.scss      # Vuetify theme customization
│   ├── App.vue         # Root component
│   └── main.js         # Application entry point
├── public/             # Static public assets
├── vite.config.mjs     # Vite configuration
├── package.json        # Dependencies and scripts
└── Dockerfile         # Docker build configuration
```

## API Integration

The client communicates with the backend server through the following API endpoints:

### Base Configuration

- **Development**: API requests are proxied through Vite dev server to `http://server:8000`
- **Production**: API requests go to the same origin (handled by reverse proxy)

### API Endpoints

#### 1. Chat Endpoint
**POST** `/api/v1/chat`

Sends natural language messages to the AI travel assistant.

**Request:**
```javascript
{
  message: "Find me a scenic route from Munich to Berlin"
}
```

**Headers:**
- `Content-Type: application/json`
- `X-Session-Id: <session_id>` (optional, for conversation continuity)

**Response:**
```javascript
{
  session_id: "uuid-string",
  message: "AI assistant response text",
  search_params: {
    origin: "München Hbf",
    destination: "Berlin Hbf",
    time: "2025-12-07T08:00:00",
    via: ["Nürnberg Hbf"],  // optional
    min_transfer_time: 10   // optional, in minutes
  }
}
```

**Usage in Code:**
```javascript
// Located in: src/stores/backendCalls.js
await backendCallsStore.fetchPrePlanForPrompt(prompt)
```

**Features:**
- Maintains conversation context via session IDs stored in localStorage
- Automatically extracts search parameters from AI responses
- Handles errors gracefully with user-friendly messages

---

#### 2. Station Search
**GET** `/api/v1/stations?q=<query>`

Searches for train stations by name with autocomplete functionality.

**Query Parameters:**
- `q` (string): Search query (minimum 2 characters)

**Response:**
```javascript
{
  stations: ["München Hbf", "München Ost", "München-Pasing", ...]
}
```

**Usage in Code:**
```javascript
// Located in: src/stores/backendCalls.js
await backendCallsStore.searchStations(query)
```

**Features:**
- Debounced search (300ms delay) to reduce API calls
- Used in autocomplete fields for origin, destination, and via stations
- Returns empty array if query is too short or search fails

---

#### 3. Connections Search
**GET** `/api/v1/connections`

Searches for train connections between stations.

**Query Parameters:**
- `start` (string, required): Origin station name
- `end` (string, required): Destination station name
- `departure_time` (string, optional): ISO format datetime (e.g., `2025-12-07T08:00:00`)
- `via` (string, optional): Intermediate station name
- `min_transfer_time` (integer, optional): Minimum transfer time in minutes

**Response:**
```javascript
{
  journeys: [
    {
      id: "journey-1",
      startStation: { name: "München Hbf", ... },
      endStation: { name: "Berlin Hbf", ... },
      legs: [
        {
          train: {
            name: "ICE 123",
            trainNumber: "123",
            path: [...],  // Intermediate stops
            wagons: [...] // Coach load data
          },
          origin: { name: "München Hbf", ... },
          destination: { name: "Nürnberg Hbf", ... },
          departureTime: "2025-12-07T08:00:00",
          arrivalTime: "2025-12-07T10:30:00",
          departurePlatform: "5",
          arrivalPlatform: "12"
        }
      ],
      transfers: 1,
      totalTime: 240,  // minutes
      aiInsight: "This journey offers scenic views..." // optional
    }
  ]
}
```

**Usage in Code:**
```javascript
// Located in: src/stores/backendCalls.js
await backendCallsStore.fetchConnections(
  origin,
  destination,
  date,        // ISO format or null
  via,         // optional
  minTransferTime  // optional
)
```

**Features:**
- Supports direct connections and multi-leg journeys
- Displays transfer information with platform details
- Shows intermediate stops for each leg
- Includes AI-generated journey insights
- Handles loading states and errors

---

## State Management

The application uses **Pinia** for centralized state management. The main store is located in `src/stores/backendCalls.js`.

### Store Structure

```javascript
{
  // State
  prePlan: null,              // AI chat response text
  prePlanParams: null,        // Extracted search parameters
  connections: [],            // Journey results array
  loading: false,             // Loading indicator
  error: null,                // Error message
  sessionId: null,            // Chat session ID (persisted in localStorage)
  
  // Actions
  fetchPrePlanForPrompt(),    // Send chat message
  fetchConnections(),         // Search for connections
  searchStations(),           // Search stations
  setSessionId()              // Update session ID
}
```

### Session Management

- Session IDs are stored in `localStorage` under the key `chat_session_id`
- Sessions persist across page refreshes
- Session ID is automatically sent in `X-Session-Id` header for chat requests

## Routing

The application uses **Vue Router 4** with automatic route generation from the `src/pages/` directory.

### Routes

- `/` - Home page (`index.vue`)
  - Chat interface for natural language queries
  - Manual search form with station autocomplete
  - Displays AI responses and extracted search parameters

- `/connections` - Journey results (`connections.vue`)
  - Displays search results from connection queries
  - Expandable journey cards with detailed leg information
  - Transfer information and platform details
  - Coach sequence visualization

- `/login` - Authentication page (`login.vue`)
  - Reserved for future authentication features

## Development Flow

### Prerequisites

- Node.js 18+ and npm
- Docker and Docker Compose (for containerized development)

### Local Development Setup

1. **Install Dependencies**
   ```bash
   cd client
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000`

3. **Development with Docker Compose**
   ```bash
   # From project root
   docker-compose up client
   ```
   This starts the client with hot-reload enabled and proxies API requests to the server container.

### Development Workflow

1. **Making Changes**
   - Edit Vue components in `src/components/` or `src/pages/`
   - Vite provides instant hot module replacement (HMR)
   - Changes are reflected immediately in the browser

2. **Adding New Components**
   - Create `.vue` files in `src/components/`
   - Import and use in pages or other components
   - Use Vuetify components for consistent styling

3. **Adding New Pages**
   - Create `.vue` files in `src/pages/`
   - Routes are automatically generated by `unplugin-vue-router`
   - File-based routing: `pages/about.vue` → `/about`

4. **API Integration**
   - Add new API calls to `src/stores/backendCalls.js`
   - Use the store in components via `useBackendCalls()`
   - Handle loading and error states

5. **Styling**
   - Use Vuetify components for Material Design UI
   - Custom styles in component `<style scoped>` blocks
   - Global theme customization in `src/styles/settings.scss`

### Build for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

### Linting

```bash
npm run lint
```

Automatically fixes ESLint issues where possible.

## Component Architecture

### Key Components

#### `NavBar.vue`
- Navigation bar component
- Displays application branding
- Can include user menu and navigation links

#### `DateTimePicker.vue`
- Custom date and time picker
- Returns formatted datetime string: `"yyyy-MM-dd HH:mm"`
- Used in manual search form

#### `CoachSequence.vue`
- Visualizes train coach/wagon layout
- Displays load indicators, amenities, and seat availability
- Receives wagon data from journey legs

#### `SeatSelection.vue`
- Seat selection interface (reserved for future use)
- Can be integrated for booking functionality

### Component Communication

- **Props Down**: Parent components pass data to children via props
- **Events Up**: Children emit events to communicate with parents
- **Store Access**: Components access shared state via Pinia stores
- **Router Navigation**: Use `useRouter()` composable for navigation

## Styling Guidelines

### Vuetify Theme

The application uses a custom Vuetify theme configured in `src/plugins/vuetify.js`:
- Primary color: Deutsche Bahn red (`#EC0016`)
- Custom typography and spacing

### Custom Styles

- Component-scoped styles use `<style scoped>`
- Global styles in `src/styles/settings.scss`
- Responsive design with Vuetify breakpoints:
  - `xs`: < 600px
  - `sm`: 600px - 960px
  - `md`: 960px - 1264px
  - `lg`: 1264px - 1904px
  - `xl`: > 1904px

## Error Handling

- API errors are caught in store actions and stored in `error` state
- User-friendly error messages displayed via Vuetify alerts
- Network errors are handled gracefully with fallback messages
- Loading states prevent duplicate requests

## Performance Optimizations

- **Debounced Search**: Station search debounced to 300ms
- **Lazy Loading**: Routes are code-split automatically
- **Vite Optimization**: Fast HMR and optimized production builds
- **Component Lazy Loading**: Heavy components can be lazy-loaded

## Browser Support

- Modern browsers with ES6+ support
- Chrome, Firefox, Safari, Edge (latest versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Environment Variables

Currently, the client uses Vite's proxy configuration for API routing. For production, configure:

- `VITE_API_BASE_URL`: Base URL for API requests (if different from origin)

## Troubleshooting

### Common Issues

1. **API requests failing**
   - Check that the server is running on port 8000
   - Verify proxy configuration in `vite.config.mjs`
   - Check browser console for CORS errors

2. **Hot reload not working**
   - Restart the dev server
   - Clear browser cache
   - Check file watcher limits (especially on Linux)

3. **Vuetify components not styling correctly**
   - Ensure Vuetify plugin is registered in `main.js`
   - Check theme configuration in `src/plugins/vuetify.js`

4. **Routes not working**
   - Verify `unplugin-vue-router` is configured correctly
   - Check that page files are in `src/pages/` directory
   - Restart dev server after adding new pages

## Future Enhancements

- [ ] User authentication and profiles
- [ ] Saved journeys and favorites
- [ ] Real-time delay notifications
- [ ] Seat booking integration
- [ ] Mobile app (PWA support)
- [ ] Offline functionality
- [ ] Multi-language support
- [ ] Accessibility improvements (ARIA labels, keyboard navigation)
