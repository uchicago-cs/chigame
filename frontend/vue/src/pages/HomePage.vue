<script setup>
import { ref } from 'vue'
import { Swiper, SwiperSlide } from 'swiper/vue'
import 'swiper/css'
import 'swiper/css/pagination'
import 'swiper/css/effect-coverflow'
import 'swiper/css/autoplay'

import { Autoplay, Pagination, EffectCoverflow } from 'swiper/modules'

import managementImg from './images/management.png'
import checkersImg from './images/checkers.png'
import wordgameImg from './images/wordgame.png'
import reversiImg from './images/reversi.png'

const tournaments = ref([
  {
    id: 1,
    name: 'Checkers Showdown',
    description: 'A classic checkers tournament for all skill levels.',
    image: checkersImg,
    status: 'Upcoming'
  },
  {
    id: 2,
    name: 'Word Masters',
    description: 'Compete in Not Wordle for the top spot!',
    image: wordgameImg,
    status: 'Ongoing'
  },
  {
    id: 3,
    name: 'Reversi Blitz',
    description: 'Fast-paced reversi action. Join now!',
    image: reversiImg,
    status: 'Completed'
  }
])

const trendingGames = ref([
  { src: managementImg, alt: 'Management' },
  { src: checkersImg, alt: 'Checkers' },
  { src: wordgameImg, alt: 'Word Game' },
  { src: reversiImg, alt: 'Reversi' }
])
</script>


<template>
<div class="hero-section">
  <div class="hero-content">
    <div class="hero">
      <p class="hero-title">Welcome to</p>
      <p class="pixeltext">Chigame.</p>
      <p class="hero-description">Make games. Play with friends. Get competitive.</p>
    </div>
  </div>
</div>
<div class="side-rect left-rect"></div>
<div class="side-rect right-rect"></div>
<img class="img-fluid logo"
     src="/logo.png"
     alt="ChiGame Logo" />
<div class="auth-buttons">
  <router-link to="login" class="auth-button">Sign Up</router-link>
  <router-link to="login" class="auth-button">Sign In</router-link>
</div>
<!-- First row of homepage for logged in users (Favorite Games and Friends List)-->
  <div class="d-flex flex-row justify-content-between">
    <!-- Favorite Games -->
    <div class="homepage-block favorite-games">
      <div class="d-flex flex-row justify-content-between">
        <span>Favorite Games</span><span class="d-flex flex-column justify-content-around"><span class="see-more-link"><a class="nav-link" href="/">>> Games</a></span></span>
      </div>
      <div class="d-flex flex-row justify-content-between game-row">
        <div class="fave-game">
          <img src="https://cf.geekdo-images.com/oWcB33sfig9QF_KBEv7iLQ__original/img/retN48ZHxCC5YaECdlWjRdWHPGs=/0x0/filters:format(png)/pic2439783.png"
               class="game-img"
               alt="battleship" />
        </div>
        <div class="fave-game">
          <img src="https://cf.geekdo-images.com/0_RWFMNapgr5yCrdhvGi_Q__original/img/c4SiusUQuh7uc0k6HDwIXYsEc8M=/0x0/filters:format(jpeg)/pic8785991.jpg"
               class="game-img"
               alt="chess" />
        </div>
        <div class="fave-game">
          <img src="https://cf.geekdo-images.com/-DHiHBBSnvaLu0Do8CIykQ__original/img/fRfoyWezpQsumExNKVxf1cwtJfg=/0x0/filters:format(jpeg)/pic8204165.jpg"
               class="game-img"
               alt="uno" />
        </div>
      </div>
      <div class="d-flex flex-row justify-content-between game-row">
        <div class="fave-game">
          <img src="https://cf.geekdo-images.com/9nGoBZ0MRbi6rdH47sj2Qg__original/img/bA8irydTCNlE38QSzM9EhcUIuNU=/0x0/filters:format(jpeg)/pic5786795.jpg"
               class="game-img"
               alt="monopoly" />
        </div>
        <div class="fave-game">
          <img src="https://cf.geekdo-images.com/tjhapy1XoNga-YGrDj4BZQ__original/img/JLkqE0LUdShELen6FBEYis1mkTs=/0x0/filters:format(png)/pic8419491.png"
               class="game-img"
               alt="hello" />
        </div>
        <div class="fave-game">
          <img src="https://cf.geekdo-images.com/dp-pJkUemCjhrwi9QItrPA__original/img/eeYPdva8ti4Hi2PYxkTLRPrtfKk=/0x0/filters:format(jpeg)/pic378237.jpg"
               class="game-img"
               alt="yahtzee" />
        </div>
      </div>
    </div>
    <!-- Friends List -->
    <div class="homepage-block friends-list flex-grow-1">
      <div class="d-flex flex-row justify-content-between">
        <span>Friends</span><span class="d-flex flex-column justify-content-around"><span class="see-more-link"><a class="nav-link" href="/">>> See all</a></span></span>
      </div>
      <div class="d-flex flex-column justify-content-between friends-list-block">
        <div class="friend d-flex flex-row justify-content-around">
          <div class="d-flex flex-column justify-content-around">
            <img src="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"
                 class="profile-pic"
                 alt="profile-pic" />
          </div>
          <div class="friend-block d-flex flex-column justify-content-around">
            <p class="friend-name">Friend Name</p>
            <p class="friend-status">Online: Currently playing [Game]</p>
            <p class="friend-status">Friend Status Message</p>
          </div>
          <div class="d-flex flex-column justify-content-around">
            <span class="dot"></span>
          </div>
        </div>
        <div class="friend d-flex flex-row justify-content-around">
          <div class="d-flex flex-column justify-content-around">
            <img src="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"
                 class="profile-pic"
                 alt="profile-pic" />
          </div>
          <div class="friend-block d-flex flex-column justify-content-around">
            <p class="friend-name">Friend Name</p>
            <p class="friend-status">Online: Currently playing [Game]</p>
            <p class="friend-status">Friend Status Message</p>
          </div>
          <div class="d-flex flex-column justify-content-around">
            <span class="dot"></span>
          </div>
        </div>
        <div class="friend d-flex flex-row justify-content-around">
          <div class="d-flex flex-column justify-content-around">
            <img src="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"
                 class="profile-pic"
                 alt="profile-pic" />
          </div>
          <div class="friend-block d-flex flex-column justify-content-around">
            <p class="friend-name">Friend Name</p>
            <p class="friend-status">Online: Currently playing [Game]</p>
            <p class="friend-status">Friend Status Message</p>
          </div>
          <div class="d-flex flex-column justify-content-around">
            <span class="dot"></span>
          </div>
        </div>
        <div class="friend d-flex flex-row justify-content-around">
          <div class="d-flex flex-column justify-content-around">
            <img src="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"
                 class="profile-pic"
                 alt="profile-pic" />
          </div>
          <div class="friend-block d-flex flex-column justify-content-around">
            <p class="friend-name">Friend Name</p>
            <p class="friend-status">Online: Currently playing [Game]</p>
            <p class="friend-status">Friend Status Message</p>
          </div>
          <div class="d-flex flex-column justify-content-around">
            <span class="dot"></span>
          </div>
        </div>
        <div class="friend d-flex flex-row justify-content-around">
          <div class="d-flex flex-column justify-content-around">
            <img src="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"
                 class="profile-pic"
                 alt="profile-pic" />
          </div>
          <div class="friend-block d-flex flex-column justify-content-around">
            <p class="friend-name">Friend Name</p>
            <p class="friend-status">Online: Currently playing [Game]</p>
            <p class="friend-status">Friend Status Message</p>
          </div>
          <div class="d-flex flex-column justify-content-around">
            <span class="dot"></span>
          </div>
        </div>
      </div>
    </div>
  </div>
<!-- Second row of homepage (Trending Games) -->
<div class="homepage-block trending-games-title flex-grow-1">
  <div class="d-flex flex-row justify-content-between">
    <span>Trending Games</span>
    <span class="d-flex flex-column justify-content-around">
      <span class="see-more-link">>> See all</span>
    </span>
  </div>
</div>
<div class="trending-games homepage-block trending-games-block">
  <Swiper
    :modules="[Pagination, EffectCoverflow, Autoplay]"
    effect="coverflow"
    :pagination="true"
    :autoplay="true"
    class="mySwiper"
    :grabCursor="true"
    :centeredSlides="true"
    slidesPerView="auto"
    :coverflowEffect="{
      rotate: 50,
      stretch: 0,
      depth: 100,
      modifier: 1,
      slideShadows: true
    }"
  >
    <SwiperSlide v-for="(game, index) in trendingGames" :key="'trend-'+index">
    <div class="game-slide">
        <img :src="game.src" :alt="game.alt" class="game-img" />
        <div class="game-name">{{ game.name }}</div>
    </div>
    </SwiperSlide>
  </Swiper>
</div>
<!-- Third row of homepage (Tournaments) -->
<div class="homepage-block tournaments">
    <div class="d-flex flex-row justify-content-between">
      <span>Tournaments</span>
      <span class="d-flex flex-column justify-content-around">
        <span class="see-more-link">
          <router-link class="nav-link" to="/tournaments">&gt;&gt; See all</router-link>
        </span>
      </span>
    </div>
    <div class="d-flex flex-row justify-content-between tournaments-block">
      <div class="tournament" v-for="tournament in tournaments" :key="tournament.id">
        <img :src="tournament.image" class="tournament-img" :alt="tournament.name" />
        <p class="tournament-name">{{ tournament.name }}</p>
        <p class="tournament-description">{{ tournament.description }}</p>
        <span class="tournament-status" :class="tournament.status.toLowerCase()">{{ tournament.status }}</span>
      </div>
    </div>
</div>
<!-- Fourth row of homepage -->
<div class="d-flex flex-row justify-content-between">
  <!-- Live Chat -->
  <div class="homepage-block live-chat flex-grow-1">
    <div class="d-flex flex-row justify-content-between">
      <span>Live Chat</span><span class="d-flex flex-column justify-content-around"><span class="see-more-link">>> See all</span></span>
    </div>
    <div class="live-chat-block tournament-name">(live chat preview here)</div>
  </div>
  <!-- Forum -->
  <div class="homepage-block forum">
    <div class="d-flex flex-row justify-content-between">
      <span>Trending Discussion</span><span class="d-flex flex-column justify-content-around"><span class="see-more-link"><a class="nav-link" href="/">>> See all</a></span></span>
    </div>
    <div class="d-flex flex-column justify-content-between forum-block">
      <div class="forum-topic d-flex flex-column justify-content-between">
        <p class="forum-post-title">Post Title</p>
        <p class="forum-post-body">Post Body</p>
        <p class="forum-post-author">Post Author</p>
      </div>
      <div class="forum-topic d-flex flex-column justify-content-between">
        <p class="forum-post-title">Post Title</p>
        <p class="forum-post-body">Post Body</p>
        <p class="forum-post-author">Post Author</p>
      </div>
      <div class="forum-topic d-flex flex-column justify-content-between">
        <p class="forum-post-title">Post Title</p>
        <p class="forum-post-body">Post Body</p>
        <p class="forum-post-author">Post Author</p>
      </div>
      <div class="forum-topic d-flex flex-column justify-content-between">
        <p class="forum-post-title">Post Title</p>
        <p class="forum-post-body">Post Body</p>
        <p class="forum-post-author">Post Author</p>
      </div>
    </div>
  </div>
</div>
</template>


<style lang="css" scoped>

.homepage-block {
font-size: 2vw;
font-weight: 500;
background-color: white;
border: 1px solid white;
border-radius: 5px;
padding: 0.5rem;
margin: 0.5rem 5rem;
}

.homepage-hero {
background-color: #F9F9F9;
border: 1px solid #D9D9D9;
border-radius: 5px;
padding: 0.5rem;
height: 75vh;
text-align: center;
}

.see-more-link {
font-size: 1vw;
font-weight: normal;
margin: 0rem;
}

.game-img {
width: 100%;
height: 100%;
object-fit: cover;
border-radius: 5px;
}

.favorite-games {
height: 65vh;
width: 54vw;
margin-right: 0.5rem;
}

.game-row {
height: 45%;
}

.fave-game {
background-color: white;
border-radius: 5px;
margin: 0.5rem;
flex: 1;
}

.friends-list {
margin-left: 0.5rem;
}

.friends-list-block {
height: 90%;
}

.friend {
flex: 1;
margin: 0.2rem;
background-color: #F9F9F9;
border: 1px solid #D9D9D9;
border-radius: 5px;
}

.friend-block {
width: 80%;
}

.dot {
height: 1vh;
width: 1vh;
background-color: #789D4A;
border-radius: 50%;
margin-right: 0.8rem;
}

.friend-name {
font-size: 1.3vw;
font-weight: normal;
margin: 0.2rem 0rem 0rem 0rem;
}

.friend-status {
font-size: 1vw;
font-weight: normal;
margin: 0rem;
}

.profile-pic {
border-radius: 100%;
object-fit: cover;
width: 6vh;
height: 6vh;
margin: 0rem 0.8rem 0rem 0.8rem;
}

.trending-games {
height: 54vh;
margin-bottom: 0.5rem;
}

.trending-games-block {
background-color: #F9F9F9;
border: 1px solid #D9D9D9;
border-radius: 5px;
padding: 0.5rem;
height: 90%;
}

.tournaments {
margin-top: 0.5rem;
margin-bottom: 2rem;
}

.tournaments-block {
display: flex;
flex-direction: row;
gap: 1.5rem;
}

.tournament {
flex: 1;
margin: 0.5rem;
background-color: white;
border-radius: 5px;
}

.tournament-img {
width: 100%;
height: 80%;
object-fit: cover;
border-radius: 5px;
}

.tournament-name {
font-size: 1.7vw;
font-weight: normal;
margin-bottom: 0rem;
}

.tournament-description {
font-size: 1.3vw;
font-weight: normal;
margin-top: 0rem;
}

.tournament-status {
  display: inline-block;
  margin-top: 0.3vw;
  padding: 0.2vw 1vw;
  border-radius: 1vw;
  font-size: 0.95vw;
  font-weight: bold;
}
.tournament-status.upcoming {
    background: #e0ffe0;
    color: #228B22;
}
.tournament-status.ongoing {
    background: #fff3cd;
    color: #856404;
}
.tournament-status.completed {
    background: #ffe5e5;
    color: #800000; }

.live-chat {
height: 60vh;
margin-right: 0.5rem;
}

.live-chat-block {
background-color: #F9F9F9;
border: 1px solid #D9D9D9;
border-radius: 5px;
padding: 0.5rem;
height: 90%;
}

.forum {
width: 54vw;
margin-left: 0.5rem;
}

.forum-block {
height: 90%;
}

.forum-topic {
flex: 1;
margin: 0.2rem;
background-color: #F9F9F9;
border: 1px solid #D9D9D9;
border-radius: 5px;
}

.forum-post-title {
font-size: 1.3vw;
font-weight: normal;
margin: 0.5rem 0.5rem 0rem 0.8rem;
}

.forum-post-body {
font-size: 1vw;
font-weight: normal;
margin: 0rem 0.5rem 0rem 0.8rem;
}

.forum-post-author {
font-size: 1vw;
font-weight: normal;
margin: 0rem 0.8rem 0.5rem 0.5rem;
text-align: right;
}

.hero-section {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 30vw;
  margin-top: 5vw;
}

.hero-content {
  z-index: 2;
  text-align: center;
  width: 50vw;
}

.side-rect {
  position: absolute;
  top: 50%;
  width: 25vw;
  height: 15vw;
  background: #800000;
  border-radius: 1vw;
  z-index: 1;
}

.left-rect {
  left: 0;
}

.right-rect {
  right: 0;
}

.logo {
  position: absolute;
  bottom: 49%;
  left: 10%;
  z-index: 10;
  width: 20%;
  height: auto;
}

.hero-title {
  font-size: 5vw;
  margin: 0;
  font-weight: bold;
}

.pixeltext {
  color: #800000;
  font-family: "Pixelify Sans", sans-serif;
  font-weight: bold;
  font-size: 7vw;
}

.hero-description {
  margin-top: 2vw;
  font-size: 2vw;
  color: #444;
  text-align: center;
}

#signin-button {
  margin-top: 2vw;
  padding: 1vw 3vw;
  font-size: 2vw;
  background-color: #800000;
  color: #fff;
  border: none;
  border-radius: 0.5vw;
  cursor: pointer;
  font-family: "Pixelify Sans", sans-serif;
  transition: background 0.3s, transform 0.2s;
}

#signin-button:hover {
  background-color: #a52a2a;
  transform: scale(1.05);
}

.auth-buttons {
  display: flex;
  justify-content: center;
  gap: 2vw;
  margin-top: 2vw;
}

.auth-button {
  padding: 1vw 3vw;
  font-size: 2vw;
  background-color: #800000;
  color: #fff;
  border: none;
  border-radius: 0.5vw;
  text-decoration: none;
  font-family: "Pixelify Sans", sans-serif;
  font-weight: bold;
  transition: background 0.3s, transform 0.2s;
  cursor: pointer;
  display: inline-block;
  text-align: center;
}

.auth-button:hover {
  background-color: #a52a2a;
  transform: scale(1.05);
}

.swiper {
  width: 100%;
  height: 100%;
  padding: 0px 64px;
  display: flex;
  align-items: cener;
  justify-content: center;
}

.swiper-slide {
  background: #fff;
  border-radius: 20px;
  width: 50%;
  height: 90%;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.swiper-slide img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 20px;
}

.trending-section {
  margin-top: 0px;
  margin-bottom: 60px;
  text-align: center;
}

.section-title {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 30px;
}

.trending-games {
  height: 60vh;
  margin: 1rem 5rem;
  background: linear-gradient(135deg,rgb(255, 255, 255) 0%, #ffffff 100%);
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.15);
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mySwiper {
  width: 90%;
  height: 90%;
}

.mySwiper .swiper-slide {
  background: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.mySwiper .swiper-slide:hover {
  transform: scale(1.1);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.35);
}

.mySwiper .game-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 15px;
  user-select: none;
  pointer-events: none;
}

.trending-games-title {
  margin-bottom: 0;
  padding-bottom: 0;
}

</style>
