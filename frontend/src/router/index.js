import Vue from 'vue'
import Router from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/UserLogin.vue'
import RegistrationForm from '../components/RegistrationForm.vue'

Vue.use(Router)

export default new Router({
    mode: 'history',
    base: process.env.BASE_URL,
    routes: [
        {
            path: '/',
            name: 'Home',
            component: Home
        },
        {
            path: '/login',
            name: 'Login',
            component: Login
        },
        {
            path: '/register',   // New route for RegistrationForm
            name: 'Register',
            component: RegistrationForm
        }
    ]
})
