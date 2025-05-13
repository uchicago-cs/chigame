<script setup>
import { ref, computed } from 'vue'

const lobbyName  = ref('')
const gameName   = ref('')
const maxPlayers = ref('')

//Random lobby data for future use and referencing
const lobbies = ref([
  {
    id: 1,
    name: 'Lobby 1',
    game: 'Chess',
    status: '',
    mods: 'None',
    createdBy: 'User1',
    createdAt: '2025-05-11 10:00',
    maxPlayers: 10
  },
  {
    id: 2,
    name: 'Lobby 2',
    game: 'Temple Run',
    status: '',
    mods: 'Modified',
    createdBy: 'User2',
    createdAt: '2025-05-11 11:00',
    maxPlayers: 8
  },
  {
    id: 3,
    name: 'Lobby 3',
    game: 'Poker',
    status: '',
    mods: 'Modified',
    createdBy: 'User3',
    createdAt: '2025-05-11 12:00',
    maxPlayers: 5
  }
])



const filtered = computed(() =>
  lobbies.value.filter(lobby => {
    const byName = lobby.name.toLowerCase().includes(lobbyName.value.toLowerCase())
    const byGame = lobby.game.toLowerCase().includes(gameName.value.toLowerCase())
    const byMax  = !maxPlayers.value || +lobby.maxPlayers <= +maxPlayers.value
    return byName && byGame && byMax
  })
)

function clearFilters () {
  lobbyName.value  = ''
  gameName.value   = ''
  maxPlayers.value = ''
}
</script>

<template>
  <div class="page">
    <h1>List of Lobbies</h1>
    <form class="filters" @submit.prevent>
      <div class="field">
        <label>Lobby Name</label>
        <input v-model="lobbyName" />
      </div>

      <div class="field">
        <label>Game Name</label>
        <input v-model="gameName" />
      </div>
      <div class="field">
        <label>Maximum Number of Players ≤</label>
        <input v-model="maxPlayers" type="number" min="1" />
      </div>

      <button type="submit">Filter</button>
      <button type="button" @click="clearFilters">Clear Filters</button>
    </form>

    <table class="lobby-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Game</th>
          <th>Match Status</th>
          <th>Game Modifications</th>
          <th>Created By</th>
          <th>Creation Time</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="lobby in filtered" :key="lobby.id">
          <td>{{ lobby.name }}</td>
          <td>{{ lobby.game }}</td>
          <td>{{ lobby.status }}</td>
          <td>{{ lobby.mods }}</td>
          <td>{{ lobby.createdBy }}</td>
          <td>{{ lobby.createdAt }}</td>
        </tr>
      </tbody>
    </table>

    <p v-if="!filtered.length" class="empty">No lobbies match those filters.</p>
  </div>
</template>

<style scoped>
.login-container {
  background: white;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-card {
  background: white;
  padding: 1.5rem;
  max-width: 360px;
  width: 100%;
}

h2 {
  margin-bottom: 1rem;
  color: #800000;
}

label {
  display: block;
  margin: 0.5rem 0 0.25rem;
  color: #737373;
}

input {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;


  background: #A6A6A6;
  border: 1px solid #A6A6A6;
  border-radius: 3px;
}

input:focus {
  outline: none;
  border-color: #800000;
}

button {
  width: 100%;
  padding: 0.6rem;
  background: #800000;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}
</style>
