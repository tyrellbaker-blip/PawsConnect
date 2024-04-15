import { createRouter, createWebHistory } from 'vue-router';

// Import views and components
import Home from '../views/HomeView.vue';
import UserLogin from '../views/UserLogin.vue';
import RegistrationForm from '../views/RegistrationForm.vue';
import UserProfile from '../views/UserProfile.vue';
import PostCreation from '../views/PostComponent.vue';
import TransferPet from '../views/TransferPet.vue';
import SearchPage from '../views/SearchPage.vue';
import FriendList from '../views/FriendManagement.vue';
import EditProfile from '../views/EditProfile.vue';
import EditPetProfile from '../components/editpetprofile.vue';

const routes = [
  {
    path: '/',
    name: 'HomeView',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: UserLogin
  },
  {
    path: '/register',
    name: 'Register',
    component: RegistrationForm
  },
  {
    path: '/user/:userId',
    name: 'UserProfile',
    component: UserProfile,
    meta: { requiresAuth: true }
  },

  {
    path: '/create-post',
    name: 'PostCreation',
    component: PostCreation,
    meta: { requiresAuth: true }
  },
  {
    path: '/transfer-pet',
    name: 'TransferPet',
    component: TransferPet,
    meta: { requiresAuth: true }
  },
  {
    path: '/search',
    name: 'SearchPage',
    component: SearchPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/friends',
    name: 'FriendList',
    component: FriendList,
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-profile',
    name: 'EditProfile',
    component: EditProfile,
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-pet-profile/:petId',
    name: 'EditPetProfile',
    component: EditPetProfile,
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

// Navigation guard to check for protected routes
router.beforeEach((to, from, next) => {
  // Check if the route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // Here you would check if the user is authenticated
    // You can modify this check according to how you handle authentication
    if (!localStorage.getItem('user-token')) {
      // Assuming you store token in localStorage
      next({
        path: '/login',
        query: { redirect: to.fullPath } // Store the full path to redirect the user back after successful login
      });
    } else {
      next();
    }
  } else {
    next(); // Always call next()!
  }
});

export default router;