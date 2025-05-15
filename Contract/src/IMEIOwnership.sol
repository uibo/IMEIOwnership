// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMEICurrency} from "../src/token.sol";
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {MessageHashUtils} from "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

contract IMEIOwnership {
    struct TradeInfo {
        address seller;
        address buyer;
        bytes32 IMEIHash;
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
    mapping(address => mapping(uint => bool)) private userNonces;
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
    function registerIMEI(address to, bytes32 IMEIHash, uint nonce, bytes calldata signature) external onlyContractOwner notRegistered(IMEIHash) {
        require(!userNonces[to][nonce], "Nonce used");
        userNonces[to][nonce] = true;

        bytes32 msgHash = MessageHashUtils.toEthSignedMessageHash(keccak256(abi.encodePacked("registerIMEI", to, IMEIHash, nonce)));
        address signer = ECDSA.recover(msgHash, signature);

        require(signer == to, "Signer discord");
        IMEIHashToOwner[IMEIHash] = signer;
    }

    // 소유권 이전
    function transferIMEI(bytes32 IMEIHash, address from, address to, uint nonce, bytes calldata signature) external {
        require(!userNonces[from][nonce], "Nonce used");
        userNonces[from][nonce] = true;

        bytes32 msgHash = MessageHashUtils.toEthSignedMessageHash(keccak256(abi.encodePacked("transferIMEI", from, to, IMEIHash, nonce)));
        address signer = ECDSA.recover(msgHash, signature);
        
        _requireIMEIOwner(IMEIHash, signer);

        IMEIHashToOwner[IMEIHash] = to;
    }

    function tradeIMEI(TradeInfo calldata tradeInfo, SellerInfo calldata sellerInfo, BuyerInfo calldata buyerInfo) external {
        require(!userNonces[tradeInfo.seller][sellerInfo.nonce], "Seller nonce used");
        userNonces[tradeInfo.seller][sellerInfo.nonce] = true;
        require(!userNonces[tradeInfo.buyer][buyerInfo.nonce], "Buyer nonce used");
        userNonces[tradeInfo.buyer][buyerInfo.nonce] = true;
        
        // 처음에 등록안해도 false인가?
        require(IMEIHashToEscrow[tradeInfo.IMEIHash].locked == false, "No such escrow");

        bytes32 msgHashSeller = MessageHashUtils.toEthSignedMessageHash(keccak256(abi.encodePacked(
            "tradeIMEI", tradeInfo.seller, tradeInfo.buyer, tradeInfo.IMEIHash, tradeInfo.price, sellerInfo.nonce
        )));
        bytes32 msgHashBuyer = MessageHashUtils.toEthSignedMessageHash(keccak256(abi.encodePacked(
            "tradeIMEI", tradeInfo.seller, tradeInfo.buyer, tradeInfo.IMEIHash, tradeInfo.price, buyerInfo.nonce
        )));

        address sellingSigner = ECDSA.recover(msgHashSeller, sellerInfo.signature);
        address buyingSigner = ECDSA.recover(msgHashBuyer, buyerInfo.signature);

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