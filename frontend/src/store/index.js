import { createStore } from 'vuex';
import auth from './modules/auth'; // Ensure this path correctly points to your auth module

const store = createStore({
    modules: {
        auth, // Include the auth module in your store
    },
    state() {
        return {
            count: 0 // General state outside of modules
        };
    },
    mutations: {
        increment(state) {
            state.count++; // Mutation to increment the count
        }
    }
});

export default store;