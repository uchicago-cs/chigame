<template>
  <nav class="navbar">
    <div class="logo">
      <img src="/logo.png" alt="Logo" class="logo" />
      <span>Chigame</span>
    </div>

    <ul class="nav-links">
      <li><router-link to="/">Home</router-link></li>
      <li><router-link to="/about">About</router-link></li>
      <li><router-link to="/forums">Forums</router-link></li>
      <li><router-link to="/lobbies">Lobbies</router-link></li>
    </ul>

    <div class="auth-btn">
      <router-link to="/login" class="sign-in">Sign In</router-link>
      <router-link to="/signup" class="sign-up">Sign Up</router-link>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavBar',
};
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #D9D9D9; /* Lightston Gray */
  padding: 1rem 2rem;
  border-bottom: 1px solid #ccc;
  font-family: 'Arial', sans-serif;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.5rem;
  font-weight: bold;
  color: #800000;
}

.logo img {
  height: 32px;
  margin-right: 0.5rem;
}

.nav-links {
  list-style: none;
  display: flex;
  gap: 1.5rem;
  padding: 0;
  margin: 0;
  margin-left: auto; /* Pushes the nav-links to the right */
}

.nav-links a {
  color: #333;
  text-decoration: none;
  font-weight: 500;
}

.nav-links a.router-link-exact-active {
  color: #800000;
  font-weight: bold;
}

.auth-btn {
  margin-left: 2rem; /* Adds space between "Lobbies" and "Sign In" */
}

.auth-btn .sign-in {
  background-color: #800000;
  color: #fff;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 600;
}
.auth-btn .sign-up {
  background-color: #fff;
  color: #800000;
  padding: 0.5rem 1rem;
  border: 1px solid #800000;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 600;
  margin-left: 0.5rem;
}

.auth-btn .sign-up:hover {
  background-color: #800000;
  color: #fff;
}

</style>
