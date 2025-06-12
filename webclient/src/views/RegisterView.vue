<template>
  <div class="register">
    <h1>IMEI 등록</h1>
    <form @submit.prevent="submitForm">
      <label>IMEI:</label>
      <div class="imei-row">
        <input v-model="imei" :disabled="imeiDisabled" required />
        <button type="button" class="toggle-btn" @click="toggleIMEI">
          {{ imeiDisabled ? '✎' : '✔' }}
        </button>
      </div>

      <label>To:</label>
      <div class='imei-row'>
        <input v-model="to" :disabled="toDisabled" required />
        <button type="button" class="toggle-btn" @click="toggleTo">
          {{ toDisabled ? '✎' : '✔'  }}
        </button>
      </div>
      <label>Nonce:</label>
      <input v-model="nonce" disabled />

      <button type="submit">등록</button>
    </form>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { makeSignature, fetch_to_and_nonce } from '@/composables/function'
import { register_imei } from '@/api/api'

const imei = ref(inject("deviceIMEI"))
const to = ref('')
const nonce = ref('')
const imeiDisabled = ref(true)
const toDisabled = ref(true)

const toggleIMEI = () => {
  imeiDisabled.value = !imeiDisabled.value
}
const toggleTo = () => {
  toDisabled.value = !toDisabled.value
}


const submitForm = async () => {
  [to.value, nonce.value] = await fetch_to_and_nonce()
  const { imei_hash, signature } = await makeSignature(imei.value, to.value, nonce.value)
  console.log("imei_hash: ", imei_hash)
  console.log("to: ", to.value)
  console.log("nonce: ", nonce.value)
  console.log("signature: ", signature)
  const payload = {
    imei_hash,
    to: to.value,
    nonce: nonce.value,
    signature
  }
  try {
    const res = await register_imei(payload)
    alert('등록 성공: ' + res)
  } catch (err) {
    alert('에러 발생: ' + err)
  }
}
</script>

<style scoped>
.register {
  max-width: 400px;
}

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

.imei-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.imei-row input {
  flex: 1;
}

.toggle-btn {
  padding: 0.4rem 0.6rem;
  font-size: 0.9rem;
  cursor: pointer;
  background-color: #ddd;
  border: 1px solid #aaa;
  border-radius: 4px;
  white-space: nowrap;
}

.toggle-btn:hover {
  background-color: #ccc;
}

button[type="submit"] {
  margin-top: 1.5rem;
  padding: 0.6rem;
  font-weight: bold;
  width: 100%;
}
</style>
