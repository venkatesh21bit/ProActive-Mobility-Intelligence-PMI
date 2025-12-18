# Hero MotoCorp Customer Mobile App

Professional React Native mobile application for Hero MotoCorp customers to monitor their motorcycle health in real-time.

## Features

### 🏍️ Vehicle Management
- View all your registered Hero MotoCorp motorcycles
- Real-time health monitoring for each vehicle
- Search vehicles by VIN number
- Quick stats dashboard (Total, Healthy, Need Service)

### 📊 Health Visualization
- Interactive motorcycle SVG diagram
- Color-coded component health indicators:
  - 🟢 Green: Healthy (≥80%)
  - 🟡 Yellow: Warning (50-79%)
  - 🔴 Red: Critical (<50%)
- Tap components to see detailed failure predictions
- Component-wise health breakdown

### 🔍 Detailed Component Analysis
- Health score for each component
- Issue detection with:
  - Failure probability
  - Estimated days to failure
  - Severity level
- Expandable component cards

### 🎨 Professional UI/UX
- Hero MotoCorp branded design (signature red color)
- Dark theme optimized for mobile viewing
- Smooth animations and transitions
- Pull-to-refresh functionality
- Responsive layout

## Technical Stack

- **Framework**: React Native (Expo)
- **Language**: JavaScript
- **UI Components**: React Native core components
- **SVG Rendering**: react-native-svg
- **HTTP Client**: Axios
- **Icons**: Ionicons (via @expo/vector-icons)

## Installation

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- Expo Go app on your mobile device (iOS/Android)

### Setup Steps

1. **Navigate to mobile directory**
   ```bash
   cd mobile
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure API endpoint**
   - Open `config.js`
   - Update the production API URL if needed (currently set to Cloud Run backend)
   ```javascript
   production: {
     apiUrl: 'https://pmi-backend-418022813675.us-central1.run.app',
     environment: 'production',
     enableLogging: false,
   }
   ```

4. **Start the development server**
   ```bash
   npm start
   ```

5. **Run on device**
   - Scan the QR code with Expo Go app (Android)
   - Scan with Camera app (iOS) which will open Expo Go

## API Integration

The app connects to the Hero MotoCorp backend API:

### Endpoints Used
- `GET /api/dashboard/vehicles` - Fetch all customer vehicles
- `GET /api/vehicles/{id}/details` - Fetch detailed vehicle health data

### Data Structure
```javascript
{
  vehicle: {
    vehicle_id: number,
    vin: string,
    make: string,
    model: string,
    year: number,
    mileage: number
  },
  health: {
    overall_score: number,
    overall_status: 'healthy' | 'warning' | 'critical',
    critical_components: number,
    warning_components: number,
    healthy_components: number
  },
  components: {
    [component_name]: {
      status: string,
      health: number,
      issues: Array<{
        probability: string,
        estimated_days: number,
        severity: string
      }>
    }
  }
}
```

## App Structure

```
mobile/
├── App.js                                    # Main app component
├── config.js                                 # Environment configuration
├── src/
│   └── components/
│       └── MotorcycleVisualization.js       # Vehicle visualization component
├── assets/                                   # Images and fonts
├── package.json                             # Dependencies
└── README.md                                # This file
```

## Key Components

### App.js
- Main navigation and state management
- Vehicle list view
- Vehicle detail view switching
- API integration and data fetching

### MotorcycleVisualization.js
- Interactive SVG motorcycle diagram
- Component health visualization
- Detailed component cards
- Issue display with predictions

## Screens

### 1. My Vehicles (Home)
- Header with Hero MotoCorp branding
- Search bar for VIN lookup
- Quick stats cards (Total, Healthy, Need Service)
- List of customer's motorcycles with:
  - Make/Model
  - VIN number
  - Year and mileage
  - Health score badge
  - View Details button

### 2. Vehicle Details
- Back button to return to list
- Vehicle information header
- Overall health status card
- Interactive motorcycle diagram with component areas
- Component health legend
- Scrollable component list with:
  - Component name and health percentage
  - Status indicator
  - Expandable issue details

## Color Scheme

Hero MotoCorp Branding:
- Primary Red: `#dc2626`, `#991b1b`
- Dark Background: `#0f172a`, `#1e293b`
- Text: `#fff`, `#94a3b8`

Health Status Colors:
- Healthy: `#22c55e` (Green)
- Warning: `#f59e0b` (Orange)
- Critical: `#ef4444` (Red)

## Development

### Running on Different Platforms

**Android:**
```bash
npm run android
```

**iOS:**
```bash
npm run ios
```

**Web:**
```bash
npm run web
```

### Environment Configuration

Edit `config.js` to switch between environments:
- `development`: Local backend (localhost:8000)
- `staging`: Staging environment
- `production`: Live Cloud Run backend

## Building for Production

### Android APK
```bash
expo build:android
```

### iOS IPA
```bash
expo build:ios
```

### Publishing Updates
```bash
expo publish
```

## Customer Features

### For Vehicle Owners
✅ View health status of all registered motorcycles
✅ See predictive maintenance alerts before failure
✅ Component-wise breakdown with visual diagram
✅ Estimated days until component failure
✅ Easy-to-understand health indicators

### Benefits
- **Proactive Maintenance**: Know issues before they become problems
- **Cost Savings**: Plan maintenance to avoid emergency repairs
- **Safety**: Stay informed about critical component health
- **Convenience**: Monitor bikes from anywhere via mobile app

## Support

For issues or questions:
- Technical Support: service@heromotocorp.com
- Customer Service: 1800-266-0018 (Toll Free)

## License

© 2025 Hero MotoCorp Ltd. All rights reserved.

---

**Powered by AI Predictive Maintenance Technology**
