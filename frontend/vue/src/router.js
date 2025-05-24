import { createRouter, createWebHistory } from 'vue-router';
import HomePage from './pages/HomePage.vue';
import AboutPage from './pages/AboutPage.vue';
import LoginPage from "./pages/LoginPage.vue";
import ForumsPage from "./pages/ForumsPage.vue";
import SignupPage from "./pages/SignupPage.vue";
import ProfilePage from "./pages/ProfilePage.vue";
import GameLibrary from "./pages/GameLibrary.vue";
import LobbiesPage from "./pages/LobbiesPage.vue";
import TournamentPage from './pages/TournamentPage.vue';

const routes = [
  { path: '/', component: HomePage },
  { path: '/about', component: AboutPage },
  {
    path: '/login',
    component: LoginPage
  },
  { path: '/forums', component: ForumsPage },
  { path: '/signup', component: SignupPage },
  { path: '/profile', component: ProfilePage },
  { path: '/games', component: GameLibrary },
  { path: '/lobbies', component: LobbiesPage },
  { path: '/tournaments', component: TournamentPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
