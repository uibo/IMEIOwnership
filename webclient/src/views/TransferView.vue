<template>
    <h1>IMEI 전송</h1>
    <form @submit.prevent="submitForm">
        <label>IMEI:</label>
        <input v-model="imei" required />
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
import { ref } from 'vue'
import { fetch_to_and_nonce, make_imei_hash, make_transfer_signature } from '@/composables/function'
import { transfer_imei } from '@/api/api'

const imei = ref('')
const from = ref('')
const to = ref('')
const nonce = ref('')

const submitForm = async () => {
  const imei_hash = make_imei_hash(imei.value)
  const [temp1, temp2] = await fetch_to_and_nonce()
  from.value = temp1.toLowerCase()
  nonce.value = temp2.toLowerCase()
  to.value = to.value.toLowerCase()
  const signature = await make_transfer_signature(imei_hash, from.value, to.value, nonce.value)
  console.log("imei_hash: ", imei_hash)
  console.log("from: ", from.value)
  console.log("to: ", to.value)
  console.log("nonce: ", nonce.value)
  console.log("signature: ", signature)
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
</style>