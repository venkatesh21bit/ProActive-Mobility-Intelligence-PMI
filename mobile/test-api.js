// Quick test to verify API connectivity
const axios = require('axios');

const API_URL = 'https://pmi-backend-418022813675.us-central1.run.app';

async function testAPI() {
  console.log('Testing API connection to:', API_URL);
  console.log('');

  try {
    // Test 1: Dashboard vehicles
    console.log('Test 1: Fetching vehicles...');
    const vehiclesResponse = await axios.get(`${API_URL}/api/dashboard/vehicles`, {
      timeout: 10000,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    });
    console.log('✅ Vehicles endpoint working!');
    console.log(`   Found ${vehiclesResponse.data.length} vehicles`);
    console.log('   First vehicle:', vehiclesResponse.data[0]?.vehicle_id);
    console.log('');

    // Test 2: Vehicle details
    if (vehiclesResponse.data.length > 0) {
      const firstVehicleId = vehiclesResponse.data[0].vehicle_id;
      console.log(`Test 2: Fetching details for vehicle ${firstVehicleId}...`);
      const detailsResponse = await axios.get(`${API_URL}/api/vehicles/${firstVehicleId}/details`, {
        timeout: 10000,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      console.log('✅ Vehicle details endpoint working!');
      console.log('   VIN:', detailsResponse.data.vin);
      console.log('   Health Score:', detailsResponse.data.health_score);
      console.log('');
    }

    console.log('🎉 All API tests passed!');
    console.log('');
    console.log('The backend is working correctly.');
    console.log('If the mobile app still shows network errors, try:');
    console.log('1. Stop the Expo server (Ctrl+C)');
    console.log('2. Clear cache: npx expo start -c');
    console.log('3. Make sure your phone and computer are on the same network');
    console.log('4. Check if your phone has internet access');

  } catch (error) {
    console.error('❌ API test failed!');
    console.error('Error:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    } else if (error.request) {
      console.error('No response received - possible network issue');
    }
  }
}

testAPI();
