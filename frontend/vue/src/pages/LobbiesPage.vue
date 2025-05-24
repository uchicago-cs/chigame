<script setup>
import { ref, computed } from 'vue'
import managementImg from './images/management.png'
import checkersImg from './images/checkers.png'
import wordgameImg from './images/wordgame.png'
import reversiImg from './images/reversi.png'
import profileImg from './images/profile_logo.png'

const search = ref('')
const gameFilter = ref('All Games')
const statusFilter = ref('Status: All')
const playerFilter = ref('Any Size')

const lobbies = ref([
  {
    id: 1,
    name: 'Checkers Pros Only',
    game: 'Checkers',
    gameImage: checkersImg,
    owner: 'Alice',
    ownerAvatar: profileImg,
    mode: 'Classic',
    currentPlayers: 2,
    maxPlayers: 2,
    status: 'Open'
  },
  {
    id: 2,
    name: 'Not Wordle Night',
    game: 'Not Wordle',
    gameImage: wordgameImg,
    owner: 'Bob',
    ownerAvatar: profileImg,
    mode: 'Hard',
    currentPlayers: 3,
    maxPlayers: 4,
    status: 'In-Game'
  },
  {
    id: 3,
    name: 'Reversi Blitz',
    game: 'Reversi',
    gameImage: reversiImg,
    owner: 'Carol',
    ownerAvatar: profileImg,
    mode: 'Blitz',
    currentPlayers: 2,
    maxPlayers: 2,
    status: 'Full'
  }
])

const filteredLobbies = computed(() => {
  return lobbies.value.filter(lobby => {
    const matchesSearch = lobby.name.toLowerCase().includes(search.value.toLowerCase())
    const matchesGame = gameFilter.value === 'All Games' || lobby.game === gameFilter.value
    const matchesStatus = statusFilter.value === 'Status: All' || lobby.status === statusFilter.value
    let matchesPlayers = true
    if (playerFilter.value === '2 Players') {
      matchesPlayers = lobby.maxPlayers === 2
    } else if (playerFilter.value === '3-4 Players') {
      matchesPlayers = lobby.maxPlayers >= 3 && lobby.maxPlayers <= 4
    } else if (playerFilter.value === '5+ Players') {
      matchesPlayers = lobby.maxPlayers >= 5
    }
    return matchesSearch && matchesGame && matchesStatus && matchesPlayers
  })
})
</script>

<template>
  <div class="lobbies-bg">
    <!-- Maroon Flare Header -->
    <div class="lobbies-flare">
      <div class="lobbies-header-content">
        <h1 class="lobbies-title">Game Lobbies</h1>
        <button class="create-lobby-btn">+ Create Lobby</button>
      </div>
      <div class="lobbies-title-underline"></div>
    </div>

    <!-- Filters -->
    <div class="lobby-filters">
      <input type="text" placeholder="Search lobbies..." class="search-bar" v-model="search">
      <select class="filter-dropdown" v-model="gameFilter">
        <option>All Games</option>
        <option>Checkers</option>
        <option>Not Wordle</option>
        <option>Reversi</option>
      </select>
      <select class="filter-dropdown" v-model="statusFilter">
        <option>Status: All</option>
        <option>Open</option>
        <option>In-Game</option>
        <option>Full</option>
      </select>
      <select class="filter-dropdown" v-model="playerFilter">
        <option>Any Size</option>
        <option>2 Players</option>
        <option>3-4 Players</option>
        <option>5+ Players</option>
      </select>
    </div>

    <!-- Lobby Cards Grid -->
    <div class="lobby-grid">
      <div
        class="lobby-card"
        v-for="lobby in filteredLobbies"
        :key="lobby.id"
      >
        <div class="lobby-card-banner">
          <img class="lobby-game-img" :src="lobby.gameImage" :alt="lobby.game" />
          <span class="lobby-game-name">{{ lobby.game }}</span>
        </div>
        <h3 class="lobby-name">{{ lobby.name }}</h3>
        <div class="lobby-details">
          <div class="lobby-owner">
            <img class="owner-avatar" :src="lobby.ownerAvatar" alt="Owner avatar" />
            <span>Owner: <b>{{ lobby.owner }}</b></span>
          </div>
          <span class="lobby-mode">{{ lobby.mode }}</span>
        </div>
        <div class="lobby-meta">
          <span class="lobby-players">
            <b>{{ lobby.currentPlayers }}</b>/<b>{{ lobby.maxPlayers }}</b> players
          </span>
          <span class="lobby-status" :class="lobby.status.toLowerCase()">{{ lobby.status }}</span>
        </div>
        <div class="lobby-actions">
          <a href="#" class="join-btn" v-if="lobby.status === 'Open'">Join</a>
          <a href="#" class="spectate-btn" v-if="lobby.status === 'In-Game'">Spectate</a>
          <span class="full-btn" v-if="lobby.status === 'Full'">Full</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lobbies-bg {
  min-height: 100vh;
  background: linear-gradient(120deg, #fff8f8 0%, #ffeaea 100%);
  padding-bottom: 4vw;
}

.lobbies-flare {
  background: linear-gradient(90deg, #800000 70%, #a52a2a 100%);
  border-radius: 0 0 2vw 2vw;
  padding: 2vw 0 1vw 0;
  box-shadow: 0 2px 12px #80000022;
  margin-bottom: 2vw;
  position: relative;
}

.lobbies-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 2vw;
}

.lobbies-title {
  color: #fff;
  font-family: "Pixelify Sans", sans-serif;
  font-size: 3vw;
  font-weight: bold;
  margin: 0;
  letter-spacing: 0.02em;
}

.lobbies-title-underline {
  width: 120px;
  height: 0.4vw;
  background: linear-gradient(90deg, #fff 60%, #ffd6d6 100%);
  border-radius: 1vw;
  margin: 1vw auto 0 auto;
}

.create-lobby-btn {
  background: #fff;
  color: #800000;
  padding: 0.7vw 2vw;
  border-radius: 0.7vw;
  border: none;
  font-weight: bold;
  font-size: 1.3vw;
  box-shadow: 0 2px 8px #80000011;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.create-lobby-btn:hover {
  background: #ffd6d6;
  color: #a52a2a;
}

.lobby-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1vw;
  justify-content: center;
  margin: 2vw auto 2vw auto;
  max-width: 1100px;
}

.search-bar, .filter-dropdown {
  padding: 0.7vw 1.2vw;
  border-radius: 0.5vw;
  border: 1.5px solid #80000033;
  font-size: 1.1vw;
  background: #fff;
  margin-bottom: 0.5vw;
  box-shadow: 0 2px 4px #80000011;
}

.lobby-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 2vw;
  justify-content: center;
  max-width: 1200px;
  margin: 0 auto;
}

.lobby-card {
  background: #fff;
  border-radius: 1vw;
  box-shadow: 0 4px 16px #80000022;
  width: 22vw;
  min-width: 260px;
  max-width: 320px;
  padding: 1.5vw 1vw 1vw 1vw;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 1vw;
  position: relative;
  transition: transform 0.15s, box-shadow 0.15s;
}
.lobby-card:hover {
  transform: translateY(-0.5vw) scale(1.03);
  box-shadow: 0 8px 32px #80000033;
}

.lobby-card-banner {
  display: flex;
  align-items: center;
  gap: 1vw;
  justify-content: center;
  margin-bottom: 0.2vw;
}
.lobby-game-img {
  width: 3vw;
  height: 3vw;
  min-width: 42px;
  min-height: 42px;
  border-radius: 0.5vw;
  object-fit: cover;
  box-shadow: 0 2px 6px #80000022;
}
.lobby-game-name {
  font-weight: bold;
  font-size: 1.1vw;
  color: #800000;
  letter-spacing: 0.01em;
}

.lobby-name {
  font-size: 1.4vw;
  font-family: "Pixelify Sans", sans-serif;
  color: #800000;
  margin: 0.2vw 0;
}

.lobby-details {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5vw;
  font-size: 1vw;
  color: #444;
  margin-bottom: 0.2vw;
}
.lobby-owner {
  display: flex;
  align-items: center;
  gap: 0.5vw;
}
.owner-avatar {
  width: 1.7vw;
  height: 1.7vw;
  min-width: 28px;
  min-height: 28px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #ffd6d6;
  box-shadow: 0 1px 4px #80000022;
}
.lobby-mode {
  background: #ffeaea;
  color: #800000;
  border-radius: 0.5vw;
  padding: 0.2vw 0.8vw;
  font-size: 0.95vw;
  font-weight: 500;
}

.lobby-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0.5vw 0 0.2vw 0;
}
.lobby-players {
  font-size: 1vw;
  color: #800000;
}
.lobby-status {
  display: inline-block;
  padding: 0.2vw 1vw;
  border-radius: 1vw;
  font-size: 0.95vw;
  font-weight: bold;
  margin-left: 0.4vw;
  letter-spacing: 0.01em;
}
.lobby-status.open { background: #e0ffe0; color: #228B22; }
.lobby-status.in-game { background: #fff3cd; color: #856404; }
.lobby-status.full { background: #ffe5e5; color: #800000; }

.lobby-actions {
  margin-top: 0.7vw;
  display: flex;
  justify-content: center;
  gap: 1vw;
}
.join-btn {
  background: #800000;
  color: #fff;
  padding: 0.4vw 1.4vw;
  border-radius: 0.4vw;
  font-size: 1.1vw;
  font-weight: bold;
  text-decoration: none;
  box-shadow: 0 2px 8px #80000011;
  transition: background 0.2s;
}
.join-btn:hover { background: #a52a2a; }
.spectate-btn {
  background: #fff3cd;
  color: #856404;
  padding: 0.4vw 1.4vw;
  border-radius: 0.4vw;
  font-size: 1.1vw;
  font-weight: bold;
  text-decoration: none;
  box-shadow: 0 2px 8px #80000011;
  transition: background 0.2s;
}
.spectate-btn:hover { background: #ffe5e5; color: #800000; }
.full-btn {
  background: #e2e3e5;
  color: #6c757d;
  padding: 0.4vw 1.4vw;
  border-radius: 0.4vw;
  font-size: 1.1vw;
  font-weight: bold;
  cursor: not-allowed;
  opacity: 0.8;
}
</style>
