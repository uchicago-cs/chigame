<template>
  <div class="signup-container">
    <div class="form-card">
      <h2>Sign Up</h2>
      <form @submit.prevent="handleSubmit">

        <label for="first-name">First Name</label>
        <input id="first-name" type="first-name" required />

        <label for="last-name">Last Name</label>
        <input id="last-name" type="last-name" required />

        <label for="email">Email</label>
        <input id="email" type="email" required />

        <label for="password">Password</label>
        <input id="password" type="password" required />

        <label for="confirm-password">Confirm Password</label>
        <input id="confirm-password" type="password" required />

        <button type="submit">Sign Up</button>
        <div class="mt-3" style="min-height: 20vh;">
          <div v-if="error">
          <div class="alert alert-danger mt-3">
              <p>{{ error }}</p>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>


<script setup>

</script>

<style scoped>
.signup-container {
  background: white;     /* page stays white */
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-card {
  background: white;     /* card stays white */
  padding: 1.5rem;
  max-width: 360px;
  width: 100%;
}

h2 {
  margin-bottom: 1rem;
  color: #800000;         /* maroon */
}

label {
  display: block;
  margin: 0.5rem 0 0.25rem;
  color: #737373;         /* dark greystone */
}

input {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;

  /* only inputs are grey */
  background: #D9D9D9;    /* light greystone */
  border: 1px solid #A6A6A6; /* greystone */
  border-radius: 3px;
}

input:focus {
  outline: none;
  border-color: #800000;  /* maroon on focus */
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
