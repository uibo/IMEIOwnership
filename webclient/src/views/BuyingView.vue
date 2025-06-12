<template>
<div class="right">
    <div class="header">
        <h2>나의 구매 거래</h2>
        <button @click="loadBuyerTrades">불러오기</button>
    </div>
    <ul class="trade-list">
    <li v-for="(trade, index) in buyerTrades" :key="index" class="trade-item">
        <p><strong>IMEI:</strong> {{ trade.tradeInfo.imei_hash }}</p>
        <p><strong>Seller:</strong> {{ trade.tradeInfo.seller }}</p>
        <p><strong>Buyer:</strong> {{ trade.tradeInfo.buyer }}</p>
        <p><strong>Price:</strong> {{ trade.tradeInfo.price }} 원</p>
        <button @click="proceed_trade(index)">거래 진행</button>
        <button @click="confirmation_trade(index)" style="margin-left: 50px;">거래 확정</button>
    </li>
    </ul>
</div>
</template>


<script setup>
import { ref } from 'vue'
import { fetch_to_and_nonce, make_buyer_signature, make_permit_vrs, make_confirm_signature } from '@/composables/function'
import { get_trades_by_buyer, match_buyerInfo, confirm_trade } from '@/api/api'
import { contractAddress } from '@/composables/contract'



const buyerTrades = ref([])

const loadBuyerTrades = async () => {
    const [temp1, temp2] = await fetch_to_and_nonce()
    const Buyer = temp1.toLowerCase()
    const payload = {
        buyer: Buyer
    }
    buyerTrades.value = (await get_trades_by_buyer(payload)).trades
}

const proceed_trade = async (index) => {
  const imei_hash = buyerTrades.value[index].tradeInfo.imei_hash
  const from = buyerTrades.value[index].tradeInfo.seller
  const price = buyerTrades.value[index].tradeInfo.price
  console.log(imei_hash)
  const [to, nonce] = await fetch_to_and_nonce()
  const signature = await make_buyer_signature(imei_hash, from, to, price, nonce)
  const [v, r, s, deadline] = await make_permit_vrs(to, contractAddress, price)
  const payload = {
    buyerInfo: {
      nonce,
      signature,
      v: String(v),
      r,
      s,
      deadline: String(deadline),
    },
    imei_hash,
  }
  console.log(payload)
  const res = await match_buyerInfo(payload)
  console.log(res)
}

const confirmation_trade = async (index) => {
  const imei_hash = buyerTrades.value[index].tradeInfo.imei_hash
  const [temp1, nonce] = await fetch_to_and_nonce()
  const signature = await make_confirm_signature(imei_hash, nonce)
  const payload = {
    imei_hash,
    nonce,
    signature,
  }
  const res = await confirm_trade(payload)
  alert("거래 종료: ", res.tx_hash)
}
</script>
<style scoped>
.trade-item p {
  font-size: 1.2rem; /* 글자 크기 키움 */
  margin: 0.3rem 0;
}

.trade-item p strong {
  white-space: nowrap; /* 'IMEI:' 줄바꿈 방지 */
}

.trade-item p:nth-child(1) {
  white-space: nowrap; /* 전체 IMEI 줄바꿈 방지 */
  overflow-x: auto;
  text-overflow: ellipsis;
}
</style>