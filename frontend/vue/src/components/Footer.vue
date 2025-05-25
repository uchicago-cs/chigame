<template>
  <footer class="mt-auto">
  <div class="d-flex flex-row">
  <div class="logo-text me-auto d-flex flex-column justify-content-between">
  <div class="d-flex flex-row">
  <img class="navbar-logo img-fluid align-top logo" src="/logo.png" alt="ChiGame Logo" />
  <span class="d-flex flex-column justify-content-around"><span class="chigame-text">Chigame</span></span>
  <span class="d-flex flex-column justify-content-around"><a class="nav-link social-media-icons" href="https://github.com/uchicago-cs/chigame"><i class="bi bi-github"></i></a></span>
  </div>
  </div>
  <ul class="navbar-nav flex-column footer-link-list one">
  <li class="nav-item">
    <router-link to="/" class="nav-link">Home</router-link>
  </li>
  <li class="nav-item">
    <router-link to="/about" class="nav-link">About</router-link>
  </li>
  <li class="nav-item">
    <router-link to="/games" class="nav-link">Games</router-link>
  </li>
  </ul>
  <ul class="navbar-nav flex-column footer-link-list two">
  <li class="nav-item">
    <router-link to="/lobbies" class="nav-link">Lobbies</router-link>
  </li>
  <li class="nav-item">
    <router-link to="/tournaments" class="nav-link">Tournaments</router-link>
  </li>
  <li class="nav-item">
    <router-link to="/forums" class="nav-link">Forums</router-link>
  </li>
  </ul>
  </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer',
};
</script>

<style scoped>
body {
  min-height: 100vh;
}

footer {
  border-top: solid 1px #D9D9D9;
}

.chigame-text {
  font-family: "Pixelify Sans", sans-serif;
  color: #800000;
  font-size: 1.8vw;
  font-weight: 600;
}

.logo-text {
  margin: 1.5rem 0rem 0rem 10rem;
  position: relative;
}

.logo {
  width: 5%;
  height: auto;
}

.footer-link-list {
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
  margin-right: 15rem;
}

.bi, .footer-link-list {
  color: #737373;
}

.bi:hover {
  color: #800000;
}

.social-media-icons {
  margin-left: 1rem;
}

a.nav-link:hover {
  color: #800000;
}
</style>
