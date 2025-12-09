// Environment configuration for mobile app
const ENV = {
  development: {
    apiUrl: 'http://localhost:8000',
    environment: 'development',
    enableLogging: true,
  },
  staging: {
    apiUrl: 'https://staging-api.yourdomain.com',
    environment: 'staging',
    enableLogging: true,
  },
  production: {
    apiUrl: 'https://your-railway-backend-url.railway.app',
    environment: 'production',
    enableLogging: false,
  },
};

const getEnvVars = (env = 'development') => {
  if (env === 'production') {
    return ENV.production;
  } else if (env === 'staging') {
    return ENV.staging;
  }
  return ENV.development;
};

// Determine environment from release channel or default to development
const environment = __DEV__ ? 'development' : 'production';

export default getEnvVars(environment);
