# Hero MotoCorp Customer App - Setup Guide

## Quick Start

### Step 1: Install Dependencies
```bash
cd mobile
npm install
```

### Step 2: Install react-native-svg
```bash
npx expo install react-native-svg
```

### Step 3: Start the App
```bash
npm start
```

### Step 4: Run on Your Device

#### Option A: Using Expo Go (Recommended for Testing)
1. Install "Expo Go" app from:
   - **Android**: [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
   - **iOS**: [App Store](https://apps.apple.com/app/expo-go/id982107779)

2. Scan the QR code shown in terminal:
   - **Android**: Use Expo Go app's QR scanner
   - **iOS**: Use Camera app (will open Expo Go)

#### Option B: Using Emulator/Simulator
```bash
# For Android Emulator
npm run android

# For iOS Simulator (Mac only)
npm run ios
```

## Troubleshooting

### Issue: "Module react-native-svg not found"
**Solution:**
```bash
npx expo install react-native-svg
```

### Issue: "Expo CLI not found"
**Solution:**
```bash
npm install -g expo-cli
```

### Issue: QR Code not scanning
**Solution:**
- Ensure phone and computer are on the same WiFi network
- Try using tunnel mode: `expo start --tunnel`

### Issue: App crashes on device
**Solution:**
- Clear Expo Go app cache
- Restart the Expo development server
- Check that backend API is accessible from your network

## Testing with Real Data

The app is pre-configured to connect to the live backend:
```
https://pmi-backend-418022813675.us-central1.run.app
```

To test:
1. Start the app
2. You should see the list of Hero MotoCorp vehicles
3. Tap any vehicle to see detailed health visualization
4. Pull down to refresh data

## For Developers

### Project Structure
```
mobile/
├── App.js                           # Main app (vehicle list + navigation)
├── src/
│   └── components/
│       └── MotorcycleVisualization.js  # Vehicle detail screen with SVG
├── config.js                        # API configuration
└── package.json                     # Dependencies
```

### Key Features Implemented
✅ Vehicle list with search
✅ Health score badges
✅ Interactive motorcycle SVG diagram
✅ Component health visualization
✅ Tap-to-expand component details
✅ Failure prediction display
✅ Pull-to-refresh
✅ Hero MotoCorp branding

### API Endpoints Used
- `GET /api/dashboard/vehicles` - Vehicle list
- `GET /api/vehicles/{id}/details` - Vehicle details

## Building Production Apps

### Android APK
```bash
expo build:android -t apk
```

### iOS App
```bash
expo build:ios
```

### EAS Build (Modern Approach)
```bash
# Install EAS CLI
npm install -g eas-cli

# Configure project
eas build:configure

# Build for Android
eas build --platform android

# Build for iOS
eas build --platform ios
```

## Publishing Updates

After making changes:
```bash
expo publish
```

Users will get updates automatically when they restart the app.

## Screenshots

The app includes:
1. **Home Screen**: List of motorcycles with health scores
2. **Detail Screen**: Interactive motorcycle diagram with component areas
3. **Component Cards**: Expandable cards showing issues and predictions

## Need Help?

- Check the main [README.md](./README.md) for detailed documentation
- Visit Hero MotoCorp service center
- Call: 1800-266-0018

---

© 2025 Hero MotoCorp Ltd.
