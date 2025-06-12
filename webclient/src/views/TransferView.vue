<template>
    <h1>IMEI 전송</h1>
    <form @submit.prevent="submitForm">
        <label>IMEI:</label>
        <input v-model="imei" required />
        <label>from:</label>
        <input v-model="from" disabled />
        <label>To:</label>
        <input v-model="to" required />
        <label>Nonce:</label>
        <input v-model="nonce" disabled />
        <button type="submit">전송</button>
    </form>
</template>

<script setup>
import { ref } from 'vue'
import { fetch_to_and_nonce } from '@/composables/function'

const imei = ref('')
const from = ref('')
const to = ref('')
const nonce = ref('')

const submitForm = async () => {
    [from.value, nonce.value] = await fetch_to_and_nonce()
    
}
</script>

<style scoped>
label {
  display: block;
  margin-top: 1rem;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 0.5rem;
  margin-top: 0.2rem;
  box-sizing: border-box;
}

button[type="submit"] {
  margin-top: 1.5rem;
  padding: 0.6rem;
  font-weight: bold;
  width: 100%;
}
</style>