<template>
  <div class="container">
    <!-- 왼쪽: 판매 등록 -->
    <div class="left">
      <h1>IMEI 거래 등록</h1>
      <form @submit.prevent="submitForm">
        <label>IMEI:</label>
        <input v-model="imei" disabled required />
        <label>Seller:</label>
        <input v-model="seller" disabled required />
        <label>Buyer:</label>
        <input v-model="buyer" required />
        <label>Price:</label>
        <input v-model="price" required />
        <label>Nonce:</label>
        <input v-model="nonce" disabled />
        <button type="submit">판매 정보 등록</button>
      </form>
    </div>
    </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { make_imei_hash, fetch_to_and_nonce, make_seller_signature } from '@/composables/function'
import { store_trade_info, get_trades_by_buyer } from '@/api/api'

const imei = ref(inject("deviceIMEI"))
const seller = ref('')
const buyer = ref('')
const price = ref('')
const nonce = ref('')

const submitForm = async () => {
    const imei_hash = make_imei_hash(imei.value)
    const [temp1, temp2] = await fetch_to_and_nonce()
    seller.value = temp1.toLowerCase()
    nonce.value = temp2.toLowerCase()
    buyer.value = buyer.value.toLowerCase()
    const signature = await make_seller_signature(imei_hash, seller.value, buyer.value, price.value, nonce.value)
    const payload = {
        tradeInfo: {
            imei_hash,
            seller: seller.value,
            buyer: buyer.value,
            price: price.value.toString(),
        },
        sellerInfo: {
            nonce: nonce.value,
            signature,
        },
    }
    try {
    const res = await store_trade_info(payload)
        alert('전송 성공: ' + res.status)
    } catch (err) {
        alert('에러 발생: ' + err)
    }
}

const loadBuyerTrades = async () => {
    const [temp1, temp2] = await fetch_to_and_nonce()
    const Buyer = temp1.toLowerCase()
    const payload = {
        buyer: Buyer
    }
    buyerTrades.value = (await get_trades_by_buyer(payload)).trades
}

</script>

<style scoped>
.container {
  display: flex;
  gap: 1rem;            /* 칸 사이 여백 */
}

/* 왼쪽은 고정 너비, 축소되지 않도록 */
.left {
  flex: 0 0 300px;      /* 너비를 300px로 고정 (원하는 크기로 조정) */
  /* 또는
  width: 300px;
  flex-shrink: 0;
  */
}

/* 오른쪽은 남은 공간을 모두 차지 */
.right {
  flex: 1;              /* flex-grow:1, flex-shrink:1, flex-basis:0 */
  overflow-y: auto;     /* 내용이 많을 때 스크롤 */
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

button[type="submit"] {
  margin-top: 1.5rem;
  padding: 0.6rem;
  font-weight: bold;
  width: 100%;
}
</style>