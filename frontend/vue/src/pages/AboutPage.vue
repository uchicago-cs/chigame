<template>
  <div class="container mt-5 mb-5">
    <div class="row justify-content-between">
      <div class="col-md-8">
        <h2 class="about-title">About Us!</h2>
        <div class="about-title-line"></div>
        <p class="about-text mt-3">Welcome to Chigame! Make games, play with friends,
          and get competitive! Started in [year], Chigame is a project developed
          by students from the CMSC 22000 Introduction to Software Development
          class at the University of Chicago.</p>
        <p class="about-text">Currently, we are working on offering Checkers, Not Wordle, and
          Interactive Fiction games that users can create and upload. For a
          more social experience, join live chats and discuss the latest tournaments
          in the forums page. We can't wait for you to find your community and
          make friends.</p>
        <p class="chigame-text mb-0">Chigame.</p>
        <p class="chigame-description mt-0">Make games. Play with friends. Get competitive.</p>
      </div>
      <div class="img-col col-md-3">
        <div class="game-card mb-3" v-for="game in games">
          <div class="square-img">
            <img :src="game.image" alt="Game cover image">
          </div>
          <h5>{{ game.title }}</h5>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  const games = ref([
      {
        id: 1,
        title: 'Checkers',
        image: '/checkerstemp.jpg'
      },
      {
        id: 2,
        title: 'Not Wordle',
        image: 'notwordletemp.jpg'
      },
    ])
</script>

<style scoped>
.container {
  padding: 0rem 10rem;
}

.chigame-text {
  color: #800000;
  font-family: "Pixelify Sans", sans-serif;
  font-weight: bold;
  font-size: 4vw;
  text-align: center;
}

.chigame-description {
  text-align: center;
  font-size: 0.8vw;
}

.about-title {
  color: #800000;
  font-weight: bold;
}

.about-title-line {
  background-color: #800000;
  width: 100%;
  height: 0.2rem;
}

.about-text {
  font-size: 1.5vw;
}

.square-img {
  position: relative;
  width: 100%;
  padding-top: 100%;
  border-radius: 0.1vw;
  box-shadow: 0.1vw 0.1vw 0.5vw #ccc;
  margin-bottom: 0.5rem;
}

.square-img img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
