<template>
    <h1>IMEI 전송</h1>
    <form @submit.prevent="submitForm">
      <div class="imei-row">
        <input v-model="imei" :disabled="imeiDisabled" required />
        <button type="button" class="toggle-btn" @click="toggleIMEI">
          {{ imeiDisabled ? '✎' : '✔' }}
        </button>
      </div>
        <label>from:</label>
        <input v-model="from" disabled required />
        <label>To:</label>
        <input v-model="to" required />
        <label>Nonce:</label>
        <input v-model="nonce" disabled />
        <button type="submit">전송</button>
    </form>
</template>

<script setup>
import { ref, inject } from 'vue'
import { fetch_to_and_nonce, make_imei_hash, make_transfer_signature } from '@/composables/function'
import { transfer_imei } from '@/api/api'

const imei = ref(inject("deviceIMEI"))
const from = ref('')
const to = ref('')
const nonce = ref('')
const imeiDisabled = ref(true)

const toggleIMEI = () => {
  imeiDisabled.value = !imeiDisabled.value
}

const submitForm = async () => {
  const imei_hash = make_imei_hash(imei.value)
  const [temp1, temp2] = await fetch_to_and_nonce()
  from.value = temp1.toLowerCase()
  nonce.value = temp2.toLowerCase()
  to.value = to.value.toLowerCase()
  const signature = await make_transfer_signature(imei_hash, from.value, to.value, nonce.value)
  const payload = {
    imei_hash,
    from_addr: from.value,
    to_addr: to.value,
    nonce: nonce.value,
    signature,
  }

  try {
    const res = await transfer_imei(payload)
    alert('전송 성공: ' + res.tx_hash)
  } catch (err) {
    alert('에러 발생: ' + err)
  }
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
</style>