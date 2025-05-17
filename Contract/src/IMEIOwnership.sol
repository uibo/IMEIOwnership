// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMEICurrency} from "../src/token.sol";
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {MessageHashUtils} from "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

contract IMEIOwnership {
    event DebugPacked(bytes packed, bytes32 msgHash, bytes32 ethMsgHash, address signer);
    struct TradeInfo {
        bytes32 IMEIHash;
        address seller;
        address buyer;
        uint price;
    }
    struct SellerInfo {
        uint nonce;
        bytes signature;
    }
    struct BuyerInfo {
        uint nonce;
        bytes signature;
        uint8 v;
        bytes32 r;
        bytes32 s;
        uint256 deadline;
    }
    struct Escrow {
        address seller;
        address buyer;
        uint256 price;
        bool locked;
    }
    mapping(address => uint256) public userNonce;
    mapping(bytes32 => address) public IMEIHashToOwner;
    mapping(bytes32 => Escrow) private IMEIHashToEscrow;
    address public contractOwner;
    IMEICurrency public token;

    constructor(address _token) {
        contractOwner = msg.sender;
        token = IMEICurrency(_token);
    }

    modifier onlyContractOwner() {
        require(msg.sender == contractOwner, "Not contract owner");
        _;
    }

    modifier notRegistered(bytes32 IMEIHash) {
        require(IMEIHashToOwner[IMEIHash] == address(0), "IMEI already registered");
        _;
    }

    function _requireIMEIOwner(bytes32 IMEIHash, address signer) view internal {
        require(IMEIHashToOwner[IMEIHash] != address(0), "IMEI not found");
        require(IMEIHashToOwner[IMEIHash] == signer, "Not IMEI owner");
    }

    // 소유자 주소 조회
    function getIMEIOwner(bytes32 IMEIHash) external view returns (address) {
        return IMEIHashToOwner[IMEIHash];
    }

    // IMEI 소유자 등록
    function registerIMEI(bytes32 IMEIHash, address to, uint nonce, bytes calldata signature) external onlyContractOwner notRegistered(IMEIHash) {
        require(nonce == userNonce[to] + 1 , "Invalid nonce");
        userNonce[to]++;
        bytes memory packedMsg = abi.encodePacked("registerIMEI", IMEIHash, to, nonce);
        bytes32 msgHash = keccak256(packedMsg);
        bytes32 ethMsgHash = MessageHashUtils.toEthSignedMessageHash(msgHash);
        address signer = ECDSA.recover(ethMsgHash, signature);

        require(signer == to, "Signer discord");
        emit DebugPacked(packedMsg, msgHash, ethMsgHash, signer);
        IMEIHashToOwner[IMEIHash] = signer;
    }

    // 소유권 이전
    function transferIMEI(bytes32 IMEIHash, address from, address to, uint nonce, bytes calldata signature) external {
        require(nonce == userNonce[from] + 1 , "Invalid nonce");
        userNonce[from]++;

        bytes32 ethMsgHash = MessageHashUtils.toEthSignedMessageHash(keccak256(abi.encodePacked("transferIMEI", IMEIHash, from, to, nonce)));
        address signer = ECDSA.recover(ethMsgHash, signature);
        
        _requireIMEIOwner(IMEIHash, signer);

        IMEIHashToOwner[IMEIHash] = to;
    }

    function tradeIMEI(TradeInfo calldata tradeInfo, SellerInfo calldata sellerInfo, BuyerInfo calldata buyerInfo) external {
        require(sellerInfo.nonce == userNonce[tradeInfo.seller] + 1, "Invalid seller nonce");
        require(buyerInfo.nonce == userNonce[tradeInfo.buyer] + 1, "Invalid buyer nonce");
        userNonce[tradeInfo.seller]++; 
        userNonce[tradeInfo.buyer]++;
        
        // 처음에 등록안해도 false인가?
        require(IMEIHashToEscrow[tradeInfo.IMEIHash].locked == false, "This IMEI is trading!");

        bytes32 ethMsgHashSeller = MessageHashUtils.toEthSignedMessageHash(keccak256(abi.encodePacked(
            "tradeIMEI", tradeInfo.IMEIHash, tradeInfo.seller, tradeInfo.buyer, tradeInfo.price, sellerInfo.nonce
        )));
        bytes32 ethMsgHashBuyer = MessageHashUtils.toEthSignedMessageHash(keccak256(abi.encodePacked(
            "tradeIMEI", tradeInfo.IMEIHash, tradeInfo.seller, tradeInfo.buyer, tradeInfo.price, buyerInfo.nonce
        )));

        address sellingSigner = ECDSA.recover(ethMsgHashSeller, sellerInfo.signature);
        address buyingSigner = ECDSA.recover(ethMsgHashBuyer, buyerInfo.signature);

        require(sellingSigner == tradeInfo.seller, "seller discord");
        require(buyingSigner == tradeInfo.buyer, "buyer discord");

        IMEIHashToOwner[tradeInfo.IMEIHash] = tradeInfo.buyer;
        require(token.balanceOf(tradeInfo.buyer) >= tradeInfo.price, "Buyer lack of Balance");
        token.permit(tradeInfo.buyer, address(this), tradeInfo.price, buyerInfo.deadline, buyerInfo.v, buyerInfo.r, buyerInfo.s);
        token.transferFrom(tradeInfo.buyer, address(this), tradeInfo.price);
        IMEIHashToEscrow[tradeInfo.IMEIHash] = Escrow(tradeInfo.seller, tradeInfo.buyer, tradeInfo.price, true);
    }

    function confirmTrade(bytes32 IMEIHash, bytes calldata signature) external {
        bytes32 msgHash = MessageHashUtils.toEthSignedMessageHash(keccak256(abi.encodePacked("confirmTrade", IMEIHash)));
        address signer = ECDSA.recover(msgHash, signature);
        require(IMEIHashToEscrow[IMEIHash].buyer == signer, "Not buyer");
        require(IMEIHashToEscrow[IMEIHash].locked == true, "Already confirmed");
        token.transfer(IMEIHashToEscrow[IMEIHash].seller, IMEIHashToEscrow[IMEIHash].price);
        delete IMEIHashToEscrow[IMEIHash];
    }
}