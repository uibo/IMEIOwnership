import { ethers } from 'ethers';
import abi from './IMEIOwnership.abi.json'

const contractAddress = '0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512';
const provider1 = new ethers.BrowserProvider(window.ethereum);
const provider2 = new ethers.JsonRpcProvider("http://127.0.0.1:8545")
export const contract_imei = new ethers.Contract(contractAddress, abi, provider2);
// provider1.send("eth_requestAccounts", []); 
// const signer = await provider1.getSigner();
// export const userAddress = await signer.getAddress();