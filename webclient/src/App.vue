<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="metamask">
        <p class="word-break-wrap">
          <strong>Account:</strong> {{ account ? account : 'disconnected' }}
        </p>
        <p v-if="account">
          <strong>Token Balance:</strong> {{ Balance }}
        </p>
        <button @click="account ? disconnectWallet() : connectWallet()">
          {{ account ? 'Disconnect' : 'Connect MetaMask' }}
        </button>
      </div>
      <h1>IMEIOwnership</h1>
      <ul>
        <li><router-link to="/">메인</router-link></li>
        <li><router-link to="/register">등록</router-link></li>
        <li><router-link to="/itemlist">조회</router-link></li>
        <li><router-link to="/transfer">전송</router-link></li>
        <li><router-link to="/trade">거래</router-link></li>
        <li><router-link to="/buy">구매</router-link></li>
      </ul>
    </aside>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getBalanceOf } from './composables/function'

const account = ref('')
const Balance = ref('Loading...')

const connectWallet = async () => {
  if (window.ethereum) {
    try {
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' })
      account.value = accounts[0]
      Balance.value = await getBalanceOf()
    } catch (err) {
      console.error(err)
    }
  } else {
    alert('Metamask not detected.')
  }
}

const disconnectWallet = () => {
  account.value = ''
}

// const truncate = (addr) => addr.slice(0, 6) + '...' + addr.slice(-4)
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 200px;
  background: #f5f5f5;
  padding: 1rem;
}

.content {
  flex: 1;
  padding: 2rem;
}
.word-break-wrap {
  word-wrap: break-word;     /* 오래된 브라우저 대응 */
  overflow-wrap: break-word; /* 최신 표준 */
  word-break: break-all;     /* 단어 중간이라도 줄바꿈 */
}
</style>
