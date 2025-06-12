import { keccak256 } from 'js-sha3'
import { contract_imei } from './contract';

export function make_imei_hash(imei) {
  const imei_hash = '0x' + keccak256('IMEI: ' + imei)
  return imei_hash
}

export async function makeSignature(imei, to, nonce) {
  const imei_hash = make_imei_hash(imei)
  to = to.toLowerCase() 
  const message = `registerIMEI ${imei_hash} to ${to} nonce ${nonce}`
  const from = (await window.ethereum.request({method: 'eth_requestAccounts'}))[0]
  const signature = await window.ethereum.request({
    method: 'personal_sign',
    params: [message, from]
  })
  return { imei_hash, signature }
}

export async function fetch_to_and_nonce() {
  const userAddress = (await window.ethereum.request({ method: 'eth_requestAccounts' }))[0]
  const rawNonce = await contract_imei.userNonce(userAddress) // BigNumber
  const validNonce = rawNonce + 1n; // BigNumber끼리 덧셈
  return [userAddress, validNonce.toString()]     // 문자열로 변환
}

