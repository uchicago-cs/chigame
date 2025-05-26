<template>
  <div class="game-library">
    <h1 class="game-title">Game Library</h1>
    <div class="game-tabs d-flex justify-content-center my-3">
      <button><span>Favorites</span></button>
      <button><span>Latest</span></button>
      <button><span>Popular</span></button>
      <button><span>Interactive Fiction</span></button>
    </div>
    <div class="game-grid">
      <div class="game-card d-flex flex-column align-items-center" v-for="game in games">
        <img :src="game.image" class="game-img" alt="Game cover image">
        <div class="game-info mb-auto text-start w-100">
          <h3>{{ game.title }}</h3>
          <div class="game-author d-flex mt-2">
            <img :src="game.authorimg" class="game-author-img" alt="Game author image">
            <div class="d-flex flex-column">
              <span class="game-author-name">{{ game.author }}</span>
              <span class="game-author-username">{{ game.username }}</span>
            </div>
          </div>
        </div>
        <button class="play-button"><span>PLAY</span></button>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  const games = ref([
    // get this info from django backend later on
    {
      id: 1,
      title: 'Checkers',
      author: 'Software Dev Adding Games Team',
      username: '@addgames',
      authorimg: '/checkerstemp.jpg',
      image: '/checkerstemp.jpg'
    },
    {
      id: 2,
      title: 'Not Wordle',
      author: 'Software Dev Adding Games II Team',
      username: '@addgamesii',
      authorimg: 'notwordletemp.jpg',
      image: 'notwordletemp.jpg'
    },
    {
      id: 2,
      title: 'Interactive Fiction 1',
      author: 'Software Dev Interactive Fiction Team',
      username: '@interactivefiction',
      authorimg: 'notwordletemp.jpg',
      image: 'notwordletemp.jpg'
    },
  ])

  // write a function for filtering games in future issue
</script>

<style scoped>
.game-library {
  text-align: center;
  background: linear-gradient(to top, #E9D0D0, #ffffff);
  padding: 2rem;
}

.game-title {
  color: #800000;
  font-weight: bold;
}

.game-tabs button {
  background: white;
  border: none;
  padding: 0.5rem 1rem;
  margin: 0 0.2rem;
  border-radius: 0.1vw;
  font-weight: bold;
  color: #800000;
  box-shadow: 0.1vw 0.1vw 0.5vw #ccc;
  transition: all 0.2s;
  transform: skew(-15deg);
}

.game-tabs span {
  display: inline-block;
  transform: skew(15deg);
}

.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(30%, 1fr));
  gap: 1.5rem;
  margin: 2rem 5rem 0rem 5rem;
}

.game-card {
  background: #ffffff;
  border: 0.1vw solid #800000;
  border-radius: 0.5vw;
  padding: 1rem;
}

.game-img {
  width: 100%;
  height: 15rem;
  object-fit: cover;
  border-radius: 0.5vw;
  margin-bottom: 0.5rem;
}

.game-author-img {
  width: 6vh;
  height: 6vh;
  border-radius: 50%;
  margin-right: 0.8rem;
}

.game-author-name {
  font-weight: bold;
  margin-right: 0.3rem;
}

.game-author-username {
  color: gray;
}

.play-button {
  margin-top: 1rem;
  background: linear-gradient(to right, #800000, #F5EAEA);
  color: white;
  border: 0.1vw solid #800000;
  padding: 0.5rem 1rem;
  border-radius: 0.1vw;
  font-weight: bold;
  transition: background 0.3s;
  transform: skew(-15deg);
  min-width: 50%;
}

.play-button:hover {
  background: #A4343A;
}

.play-button span {
  display: inline-block;
  transform: skew(15deg);
  font-size: 1.2vw;
}
</style>
