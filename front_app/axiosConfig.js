import axios from 'axios';

// Create an Axios instance with a default base URL
const axiosInstance = axios.create({
  baseURL: 'http://localhost:5000/api', // Set the base URL for all requests
});

// You can also set default headers here if needed
// axiosInstance.defaults.headers.common['Authorization'] = 'Bearer token';

// Export the Axios instance to use it in other parts of the app
export default axiosInstance;
