import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.provide("deviceIMEI", "123456789012345")
app.use(router)
app.mount('#app')
