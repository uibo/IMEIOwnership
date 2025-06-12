import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ItemListView from '../views/ItemListView.vue'
import RegisterView from '../views/RegisterView.vue'
import TransferView from '../views/TransferView.vue'
import TradeView from '@/views/TradeView.vue'
import BuyingView from '@/views/BuyingView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
    {
    path:'/register',
    name:'register',
    component: RegisterView
  },
  {
    path:'/itemlist',
    name:'itemlist',
    component: ItemListView
  },
  {
    path:'/transfer',
    name:'transfer',
    component: TransferView,
  },
  {
    path:'/trade',
    name:'trade',
    component: TradeView,
  },
  {
    path:'/buy',
    name:'buy',
    component: BuyingView,
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes
})

export default router
