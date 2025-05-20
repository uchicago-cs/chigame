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
<div class="homepage-block trending-games">
  <div class="d-flex flex-row justify-content-between">
    <span>Trending Games</span><span class="d-flex flex-column justify-content-around"><span class="see-more-link"><a class="nav-link" href="/">>> See all</a></span></span>
  </div>
  <div class="trending-games-block tournament-name">
    <img src="https://cf.geekdo-images.com/9nGoBZ0MRbi6rdH47sj2Qg__original/img/bA8irydTCNlE38QSzM9EhcUIuNU=/0x0/filters:format(jpeg)/pic5786795.jpg"
         class="game-img"
         alt="monopoly" />
  </div>
</div>
<!-- Third row of homepage (Tournaments) -->
<div class="homepage-block tournaments">
  <div class="d-flex flex-row justify-content-between">
    Tournaments
    <span class="d-flex flex-column justify-content-around"><span class="see-more-link"><a class="nav-link" href="/">>> See all</a></span></span>
  </div>
  <div class="d-flex flex-row justify-content-between tournaments-block">
    <div class="tournament">
      <img src="https://cf.geekdo-images.com/oWcB33sfig9QF_KBEv7iLQ__original/img/retN48ZHxCC5YaECdlWjRdWHPGs=/0x0/filters:format(png)/pic2439783.png"
           class="tournament-img"
           alt="battleship" />
      <p class="tournament-name">Tournament Name</p>
      <p class="tournament-description">Tournament Description</p>
    </div>
    <div class="tournament">
      <img src="https://cf.geekdo-images.com/0_RWFMNapgr5yCrdhvGi_Q__original/img/c4SiusUQuh7uc0k6HDwIXYsEc8M=/0x0/filters:format(jpeg)/pic8785991.jpg"
           class="tournament-img"
           alt="chess" />
      <p class="tournament-name">Tournament Name</p>
      <p class="tournament-description">Tournament Description</p>
    </div>
    <div class="tournament">
      <img src="https://cf.geekdo-images.com/-DHiHBBSnvaLu0Do8CIykQ__original/img/fRfoyWezpQsumExNKVxf1cwtJfg=/0x0/filters:format(jpeg)/pic8204165.jpg"
           class="tournament-img"
           alt="uno" />
      <p class="tournament-name">Tournament Name</p>
      <p class="tournament-description">Tournament Description</p>
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
height: 60vh;
margin-top: 0.5rem;
}

.tournaments-block {
height: 90%;
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

</style>
