import { createRouter, createWebHistory } from 'vue-router';
import HomePage from './pages/HomePage.vue';
import AboutPage from './pages/AboutPage.vue';
import LoginPage from "./pages/LoginPage.vue";
import ForumsPage from "./pages/ForumsPage.vue";
import SignupPage from "./pages/SignupPage.vue";

const routes = [
  { path: '/', component: HomePage },
  { path: '/about', component: AboutPage },
  {
    path: '/login',
    component: LoginPage
  },
  { path: '/forums', component: ForumsPage },
  { path: '/signup', component: SignupPage },

];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
