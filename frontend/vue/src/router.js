import { createRouter, createWebHistory } from 'vue-router';
import HomePage from './pages/HomePage.vue';
import AboutPage from './pages/AboutPage.vue';
import LoginPage from "./pages/LoginPage.vue";

const routes = [
  { path: '/', component: HomePage },
  { path: '/about', component: AboutPage },
  {
    path: '/login',
    component: LoginPage
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
