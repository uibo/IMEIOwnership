// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMEICurrency} from "../src/IMEICurrency.sol";
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {MessageHashUtils} from "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
import {Strings} from "@openzeppelin/contracts/utils/Strings.sol";

contract IMEIOwnership {
    struct TradeInfo {
        bytes32 imeiHash;
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
        bool isPending;
    }
    mapping(address => uint256) public userNonce;
    mapping(bytes32 => address) public imeiHashToOwner;
    mapping(bytes32 => Escrow) private imeiHashToEscrow;
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

    modifier notRegistered(bytes32 imeiHash) {
        require(imeiHashToOwner[imeiHash] == address(0), "IMEI already registered");
        _;
    }

    function _onlyIMEIOwner(bytes32 imeiHash, address signer) view internal {
        require(imeiHashToOwner[imeiHash] == signer, "Not IMEI owner");
    }

    function _validNonce(address user, uint nonce) internal {
        require(nonce == userNonce[user] + 1, "Invalid nonce");
        userNonce[user]++;
    }

    function _recoverSigner(bytes memory message, bytes memory signature) internal pure returns (address) {
        bytes32 ethSignMsgHash = MessageHashUtils.toEthSignedMessageHash(message);
        return ECDSA.recover(ethSignMsgHash, signature);
    }


    // function getIMEIOwner(bytes32 imeiHash) external view returns (address) {
    //     require(imeiHashToOwner[imeiHash] != address(0), "IMEI not registered");
    //     return imeiHashToOwner[imeiHash];
    // }

    function registerIMEI(bytes32 imeiHash, address to, uint nonce, bytes calldata signature) external onlyContractOwner notRegistered(imeiHash) {
        _validNonce(to, nonce);
        string memory str_imeiHash = Strings.toHexString(uint256(imeiHash));
        string memory str_to = Strings.toHexString(to);
        string memory str_nonce = Strings.toString(nonce);
        bytes memory message = abi.encodePacked("registerIMEI ", str_imeiHash, " to ", str_to, " nonce ", str_nonce);
        address signer = _recoverSigner(message, signature);
        require(signer == to, "Signer discord");
        imeiHashToOwner[imeiHash] = signer;
    }

    function transferIMEI(bytes32 imeiHash, address from, address to, uint nonce, bytes calldata signature) external {
        _validNonce(from, nonce);
        string memory str_imeiHash = Strings.toHexString(uint256(imeiHash));
        string memory str_from = Strings.toHexString(from);
        string memory str_to = Strings.toHexString(to);
        string memory str_nonce = Strings.toString(nonce);
        bytes memory message = abi.encodePacked("transferIMEI ", str_imeiHash, " from ", str_from, " to ", str_to, " nonce ", str_nonce);
        address signer = _recoverSigner(message, signature);
        require(signer == from, "Signer discord");
        _onlyIMEIOwner(imeiHash, signer);
        imeiHashToOwner[imeiHash] = to; 
    }

    function tradeIMEI(TradeInfo calldata tradeInfo, SellerInfo calldata sellerInfo, BuyerInfo calldata buyerInfo) external {
        _validNonce(tradeInfo.seller, sellerInfo.nonce);
        _validNonce(tradeInfo.buyer, buyerInfo.nonce);
        
        require(imeiHashToEscrow[tradeInfo.imeiHash].isPending == false, "This IMEI is trading!");
        string memory str_imeiHash = Strings.toHexString(uint256(tradeInfo.imeiHash));
        string memory str_from = Strings.toHexString(tradeInfo.seller);
        string memory str_to = Strings.toHexString(tradeInfo.buyer);
        string memory str_price = Strings.toString(tradeInfo.price);
        string memory str_sellerInfo_nonce = Strings.toString(sellerInfo.nonce);
        bytes memory sellerMessage = abi.encodePacked(
            "tradeIMEI ", str_imeiHash,
            " from ", str_from ,
            " to ", str_to,
            " price ", str_price,
            " nonce ", str_sellerInfo_nonce
        );
        string memory str_buyerInfo_nonce = Strings.toString(buyerInfo.nonce);
        bytes memory buyerMessage = abi.encodePacked(
            "tradeIMEI ", str_imeiHash,
            " from ", str_from, 
            " to ", str_to,
            " price ", str_price, 
            " nonce ", str_buyerInfo_nonce
        );
        address sellerSigner = _recoverSigner(sellerMessage, sellerInfo.signature);
        address buyerSigner = _recoverSigner(buyerMessage, buyerInfo.signature);
        require(sellerSigner == tradeInfo.seller, "seller discord");
        require(buyerSigner == tradeInfo.buyer, "buyer discord");

        imeiHashToOwner[tradeInfo.imeiHash] = tradeInfo.buyer;
        require(token.balanceOf(tradeInfo.buyer) >= tradeInfo.price, "Buyer lack of Balance");
        token.permit(tradeInfo.buyer, address(this), tradeInfo.price, buyerInfo.deadline, buyerInfo.v, buyerInfo.r, buyerInfo.s);
        token.transferFrom(tradeInfo.buyer, address(this), tradeInfo.price);
        imeiHashToEscrow[tradeInfo.imeiHash] = Escrow(tradeInfo.seller, tradeInfo.buyer, tradeInfo.price, true);
    }

    function confirmTrade(bytes32 imeiHash, uint nonce, bytes calldata signature) external {
        string memory str_imeiHash = Strings.toHexString(uint256(imeiHash));
        string memory str_nonce = Strings.toString(nonce);
        bytes memory message = abi.encodePacked("confirmTrade ", str_imeiHash, " nonce ", str_nonce);
        address buyerSigner = _recoverSigner(message, signature);
        require(imeiHashToEscrow[imeiHash].buyer == buyerSigner, "Not buyer");
        require(imeiHashToEscrow[imeiHash].isPending == true, "Trade already completed");
        token.transfer(imeiHashToEscrow[imeiHash].seller, imeiHashToEscrow[imeiHash].price);
        delete imeiHashToEscrow[imeiHash];
    }
}