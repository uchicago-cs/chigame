<template>
  <div id="app">
    <NavBar />
    <router-view />
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue';

export default {
  name: 'App',
  components: {
    NavBar,
  },
};
</script>

<style>
/* You can move any shared app-level styles here if needed */
body {
  margin: 0;
  font-family: Arial, sans-serif;
}
</style>
