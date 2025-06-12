import { keccak256 } from 'js-sha3'
import { contract_imei, contract_currency, provider1, contract_currency1, contractAddress_currency } from './contract';
import { ethers } from 'ethers';

export function make_imei_hash(imei) {
  const imei_hash = '0x' + keccak256('IMEI: ' + imei)
  return imei_hash
}

export async function makeSignature(imei, to, nonce) {
  const imei_hash = make_imei_hash(imei)
  to = to.toLowerCase() 
  const message = `registerIMEI ${imei_hash} to ${to} nonce ${nonce}`
  const signer = (await window.ethereum.request({method: 'eth_requestAccounts'}))[0]
  const signature = await window.ethereum.request({
    method: 'personal_sign',
    params: [message, signer]
  })
  return { imei_hash, signature }
}

export async function make_transfer_signature(imei_hash, from, to, nonce) {
  from = from.toLowerCase()
  to = to.toLowerCase()
  const message = `transferIMEI ${imei_hash} from ${from} to ${to} nonce ${nonce}`
  const signer = (await window.ethereum.request({method: 'eth_requestAccounts'}))[0]
  const signature = await window.ethereum.request({
    method: 'personal_sign',
    params: [message, signer]
  })
  return signature
}

export async function make_seller_signature(imei_hash, from, to, price, nonce) {
  from = from.toLowerCase()
  to = to.toLowerCase()
  const message = `tradeIMEI ${imei_hash} from ${from} to ${to} price ${price} nonce ${nonce}`
  const signer = (await window.ethereum.request({method: 'eth_requestAccounts'}))[0]
  const signature = await window.ethereum.request({
    method: 'personal_sign',
    params: [message, signer]
  })
  return signature
}

export async function make_buyer_signature(imei_hash, from, to, price, nonce) {
  from = from.toLowerCase()
  to = to.toLowerCase()
  const message = `tradeIMEI ${imei_hash} from ${from} to ${to} price ${price} nonce ${nonce}`
  const signer = (await window.ethereum.request({method: 'eth_requestAccounts'}))[0]
  const signature = await window.ethereum.request({
    method: 'personal_sign',
    params: [message, signer]
  })
  return signature
}

export async function fetch_to_and_nonce() {
  const userAddress = (await window.ethereum.request({ method: 'eth_requestAccounts' }))[0]
  const rawNonce = await contract_imei.userNonce(userAddress) // BigNumber
  const validNonce = rawNonce + 1n; // BigNumber끼리 덧셈
  return [userAddress, validNonce.toString()]     // 문자열로 변환
}

export async function getBalanceOf() {
  const userAddress = (await window.ethereum.request({ method: 'eth_requestAccounts' }))[0]
  const balance = await contract_currency.balanceOf(userAddress)
  return balance.toString()
}

export async function make_permit_vrs(owner, spender, value) {
  const signer = await provider1.getSigner()
  const token = contract_currency1

  const name = await token.name()
  const version = '1'
  const chainId = (await provider1.getNetwork()).chainId
  const nonce = await token.nonces(owner)
  const deadline = Math.floor(Date.now() / 1000) + 3600

  const domain = {
    name,
    version,
    chainId,
    verifyingContract: contractAddress_currency,
  }

  const types = {
    Permit: [
      { name: 'owner', type: 'address' },
      { name: 'spender', type: 'address' },
      { name: 'value', type: 'uint256' },
      { name: 'nonce', type: 'uint256' },
      { name: 'deadline', type: 'uint256' },
    ],
  }
  const message = {
    owner,
    spender,
    value,
    nonce,
    deadline,
  }

  const signature = await signer.signTypedData(domain, types, message)

  // ✂️ v, r, s 분리
  const { v, r, s } = ethers.Signature.from(signature)
  return [v, r, s, deadline]
}

export async function make_confirm_signature(imei_hash, nonce) {
  const message = `confirmTrade ${imei_hash} nonce ${nonce}`
  const signer = (await window.ethereum.request({method: 'eth_requestAccounts'}))[0]
  const signature = await window.ethereum.request({
    method: 'personal_sign',
    params: [message, signer]
  })
  return signature
}

