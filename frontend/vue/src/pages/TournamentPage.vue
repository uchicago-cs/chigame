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
const dateFilter = ref('Any Date')

const tournaments = ref([
  {
    id: 1,
    name: 'Checkers Showdown',
    date: '2025-06-01',
    status: 'Upcoming',
    image: checkersImg,
    game: 'Checkers'
  },
  {
    id: 2,
    name: 'Word Masters',
    date: '2025-06-15',
    status: 'Ongoing',
    image: wordgameImg,
    game: 'Not Wordle'
  },
  {
    id: 3,
    name: 'Reversi Blitz',
    date: '2025-07-01',
    status: 'Completed',
    image: reversiImg,
    game: 'Reversi'
  }
])

const filteredTournaments = computed(() => {
  return tournaments.value.filter(t => {
    const matchesSearch = t.name.toLowerCase().includes(search.value.toLowerCase())
    const matchesGame = gameFilter.value === 'All Games' || t.game === gameFilter.value
    const matchesStatus = statusFilter.value === 'Status: All' || t.status === statusFilter.value
    // For future: date filtering logic can be added here
    return matchesSearch && matchesGame && matchesStatus
  })
})
</script>

<template>
  <div class="tournaments-bg">
    <!-- Maroon Flare Header -->
    <div class="tournaments-flare">
      <div class="tournaments-header-content">
        <h1 class="tournaments-title">Tournaments</h1>
        <button class="create-tournament-btn">+ Create Tournament</button>
      </div>
      <div class="tournaments-title-underline"></div>
    </div>

    <!-- Filters -->
    <div class="tournament-filters">
      <input type="text" placeholder="Search tournaments..." class="search-bar" v-model="search">
      <select class="filter-dropdown" v-model="gameFilter">
        <option>All Games</option>
        <option>Checkers</option>
        <option>Not Wordle</option>
        <option>Reversi</option>
      </select>
      <select class="filter-dropdown" v-model="statusFilter">
        <option>Status: All</option>
        <option>Upcoming</option>
        <option>Ongoing</option>
        <option>Completed</option>
      </select>
      <!-- For future: add date filter if needed -->
    </div>

    <!-- Tournament Cards Grid -->
    <div class="tournament-grid">
      <div
        class="tournament-card"
        v-for="tournament in filteredTournaments"
        :key="tournament.id"
      >
        <div class="tournament-card-banner">
          <img class="tournament-game-img" :src="tournament.image" :alt="tournament.game" />
          <span class="tournament-game-name">{{ tournament.game }}</span>
        </div>
        <h3 class="tournament-name">{{ tournament.name }}</h3>
        <div class="tournament-details">
          <span class="tournament-date">{{ tournament.date }}</span>
          <span class="tournament-status" :class="tournament.status.toLowerCase()">{{ tournament.status }}</span>
        </div>
        <div class="tournament-actions">
          <a href="#" class="register-btn" v-if="tournament.status === 'Upcoming'">Register</a>
          <a href="#" class="bracket-btn">View Bracket</a>
          <a href="#" class="watch-btn" v-if="tournament.status !== 'Upcoming'">Watch Live</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tournaments-bg {
  min-height: 100vh;
  background: linear-gradient(120deg, #fff8f8 0%, #ffeaea 100%);
  padding-bottom: 4vw;
}

.tournaments-flare {
  background: linear-gradient(90deg, #800000 70%, #a52a2a 100%);
  border-radius: 0 0 2vw 2vw;
  padding: 2vw 0 1vw 0;
  box-shadow: 0 2px 12px #80000022;
  margin-bottom: 2vw;
  position: relative;
}

.tournaments-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 2vw;
}

.tournaments-title {
  color: #fff;
  font-family: "Pixelify Sans", sans-serif;
  font-size: 3vw;
  font-weight: bold;
  margin: 0;
  letter-spacing: 0.02em;
}

.tournaments-title-underline {
  width: 120px;
  height: 0.4vw;
  background: linear-gradient(90deg, #fff 60%, #ffd6d6 100%);
  border-radius: 1vw;
  margin: 1vw auto 0 auto;
}

.create-tournament-btn {
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
.create-tournament-btn:hover {
  background: #ffd6d6;
  color: #a52a2a;
}

.tournament-filters {
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

.tournament-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 2vw;
  justify-content: center;
  max-width: 1200px;
  margin: 0 auto;
}

.tournament-card {
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
.tournament-card:hover {
  transform: translateY(-0.5vw) scale(1.03);
  box-shadow: 0 8px 32px #80000033;
}

.tournament-card-banner {
  display: flex;
  align-items: center;
  gap: 1vw;
  justify-content: center;
  margin-bottom: 0.2vw;
}
.tournament-game-img {
  width: 3vw;
  height: 3vw;
  min-width: 42px;
  min-height: 42px;
  border-radius: 0.5vw;
  object-fit: cover;
  box-shadow: 0 2px 6px #80000022;
}
.tournament-game-name {
  font-weight: bold;
  font-size: 1.1vw;
  color: #800000;
  letter-spacing: 0.01em;
}

.tournament-name {
  font-size: 1.4vw;
  font-family: "Pixelify Sans", sans-serif;
  color: #800000;
  margin: 0.2vw 0;
}

.tournament-details {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5vw;
  font-size: 1vw;
  color: #444;
  margin-bottom: 0.2vw;
}
.tournament-date {
  background: #ffeaea;
  color: #800000;
  border-radius: 0.5vw;
  padding: 0.2vw 0.8vw;
  font-size: 0.95vw;
  font-weight: 500;
}
.tournament-status {
  display: inline-block;
  padding: 0.2vw 1vw;
  border-radius: 1vw;
  font-size: 0.95vw;
  font-weight: bold;
  margin-left: 0.4vw;
  letter-spacing: 0.01em;
}
.tournament-status.upcoming { background: #e0ffe0; color: #228B22; }
.tournament-status.ongoing { background: #fff3cd; color: #856404; }
.tournament-status.completed { background: #ffe5e5; color: #800000; }

.tournament-actions {
  margin-top: 0.7vw;
  display: flex;
  justify-content: center;
  gap: 1vw;
}
.register-btn {
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
.register-btn:hover { background: #a52a2a; }
.bracket-btn {
  background: #f8d7da;
  color: #800000;
  padding: 0.4vw 1.4vw;
  border-radius: 0.4vw;
  font-size: 1.1vw;
  font-weight: bold;
  text-decoration: none;
  box-shadow: 0 2px 8px #80000011;
  transition: background 0.2s;
}
.bracket-btn:hover { background: #ffe5e5; color: #800000; }
.watch-btn {
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
.watch-btn:hover { background: #ffe5e5; color: #800000; }
</style>
