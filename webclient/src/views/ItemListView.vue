<template>
  <h1>IMEI 조회</h1>
  <br />
  <h2 style="white-space: nowrap;">현재 장치의 IMEI: {{ deviceIMEI }}</h2>
  <h3>현재 장치의 IMEI_hash: {{ imeiHash }}</h3>
  <br />
  <br />
  <h3>IMEI 소유자 조회</h3>
  <form @submit.prevent="submitForm" class="form-row">
    <label for="imei">IMEI:</label>
    <input v-model="imei" id="imei" required />
    <button type="submit">조회</button>
  </form>
  <div v-if="result">
    <p>IMEI: {{ imei }}</p>
    <p>Owner: {{ result }}</p>
  </div>
</template>


<script setup>
import { ref, inject, onMounted } from 'vue'
import { make_imei_hash } from '@/composables/function'
import { get_imei_owner } from '@/api/api'

const deviceIMEI = inject("deviceIMEI")

const imei = ref('')
const imeiHash = ref('')
const result = ref(null)

const submitForm = async () => {
    const imei_hash = make_imei_hash(imei.value)
    const payload = {imei_hash}
  try {
    const res = await get_imei_owner(payload)
    result.value = res
  } catch (err) {
    result.value = null
  }
}

onMounted(async() => {
  imeiHash.value = await make_imei_hash(deviceIMEI);
})

</script>

<style scoped>
.form-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

input {
  flex: 1;
  padding: 0.4rem;
  font-size: 14px;
}

button {
  padding: 0.4rem 1rem;
  font-size: 14px;
  font-weight: bold;
  white-space: nowrap;
}
</style>
