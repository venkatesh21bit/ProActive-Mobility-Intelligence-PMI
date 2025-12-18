// Environment configuration for mobile app
const ENV = {
  development: {
    apiUrl: 'http://localhost:8000',
    environment: 'development',
    enableLogging: true,
  },
  staging: {
    apiUrl: 'https://pmi-backend-418022813675.us-central1.run.app',
    environment: 'staging',
    enableLogging: true,
  },
  production: {
    apiUrl: 'https://pmi-backend-418022813675.us-central1.run.app',
    environment: 'production',
    enableLogging: false,
  },
};

const getEnvVars = (env = 'production') => {
  if (env === 'production') {
    return ENV.production;
  } else if (env === 'staging') {
    return ENV.staging;
  }
  return ENV.development;
};

// Determine environment from release channel or default to production
// For Expo Go development, we'll use production backend since there's no local backend
const environment = 'production'; // Changed from __DEV__ ? 'development' : 'production'

export default getEnvVars(environment);
