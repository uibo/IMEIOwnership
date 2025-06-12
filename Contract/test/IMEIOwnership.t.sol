// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {IMEICurrency} from "../src/IMEICurrency.sol";
import {IMEIOwnership} from "../src/IMEIOwnership.sol";
import {MessageHashUtils} from "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
import {Strings} from "@openzeppelin/contracts/utils/Strings.sol";
import {IERC20Permit} from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Permit.sol";

contract IMEIOwnershipTest is Test {
    address seller = 0x70997970C51812dc3A010C7d01b50e0d17dc79C8;
    uint256 sellerPrivate = 0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d;
    address buyer = 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC;
    uint256 buyerPrivate = 0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a;
    bytes32 imeiHash = keccak256("IMEI: 123456789012345");
    IMEICurrency imeiCurrency;
    IMEIOwnership imeiOwnership;
    uint sellerNonce;
    uint buyerNonce;

    function setUp() public {
        imeiCurrency = new IMEICurrency();
        imeiOwnership = new IMEIOwnership(address(imeiCurrency));
        sellerNonce = imeiOwnership.userNonce(seller) + 1;
        buyerNonce = imeiOwnership.userNonce(buyer) + 1;

    }

    function makeSignature(bytes memory message, uint256 privateKey) internal pure returns (bytes memory) {
        bytes32 ethSignMsgHash = MessageHashUtils.toEthSignedMessageHash(keccak256(message));
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(privateKey, ethSignMsgHash);
        return abi.encodePacked(r, s, v);
    }

    function makePermitSignature(
        address token,        // ERC20Permit 토큰 주소
        address owner,        // 서명자 = buyer
        address spender,      // 예: address(imeiOwnership)
        uint256 value,        // 승인할 금액
        uint256 deadline,     // 유효 시한
        uint256 privateKey    // 서명자의 개인 키 (uint256)
    ) internal view returns (uint8 v, bytes32 r, bytes32 s) {
        IERC20Permit permitToken = IERC20Permit(token);
        uint256 nonce = permitToken.nonces(owner);
        bytes32 domainSeparator = permitToken.DOMAIN_SEPARATOR();
        bytes32 structHash = keccak256(abi.encode(
            keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"),
            owner,
            spender,
            value,
            nonce,
            deadline
        ));

        bytes32 digest = keccak256(abi.encodePacked(
            "\x19\x01",
            domainSeparator,
            structHash
        ));

        return vm.sign(privateKey, digest);
    }

    function test_registerIMEI() public {
        bytes memory message = abi.encodePacked("registerIMEI ", imeiHash, " to ", seller, " (nonce: ", Strings.toString(sellerNonce), ")");
        bytes memory sig = makeSignature(message, sellerPrivate);
        assertTrue(imeiOwnership.imeiHashToOwner(imeiHash) == address(0));
        imeiOwnership.registerIMEI(imeiHash, seller, sellerNonce, sig);
        assertEq(imeiOwnership.imeiHashToOwner(imeiHash), seller);
    }

    function test_getIMEIOwner() public {
        test_registerIMEI();
        assertEq(imeiOwnership.imeiHashToOwner(imeiHash), seller);
    }

    function test_transferIMEI() public {
        test_registerIMEI();
        sellerNonce = imeiOwnership.userNonce(seller) + 1;
        bytes memory message = abi.encodePacked("transferIMEI ", imeiHash, " from ", seller, " to ", buyer, " (nonce: ", Strings.toString(sellerNonce), ")");
        bytes memory sig = makeSignature(message, sellerPrivate);
        imeiOwnership.transferIMEI(imeiHash, seller, buyer, sellerNonce, sig);
        assertEq(imeiOwnership.imeiHashToOwner(imeiHash), buyer);
    }

    function test_tradeIMEI() public {
        test_registerIMEI();
        sellerNonce = imeiOwnership.userNonce(seller) + 1;
        uint price = 100000;
        imeiCurrency.mint(buyer, price);
        assertEq(imeiCurrency.balanceOf(buyer), price);
        IMEIOwnership.TradeInfo memory tradeInfo = IMEIOwnership.TradeInfo(imeiHash, seller, buyer, price);

        bytes memory sellerMessage = abi.encodePacked(
            "tradeIMEI ", imeiHash, 
            " from ", seller, 
            " to ", buyer, 
            " price: ", Strings.toString(price),
            " (nonce: ", Strings.toString(sellerNonce), ")"
        );
        bytes memory sellerSig = makeSignature(sellerMessage, sellerPrivate);
        IMEIOwnership.SellerInfo memory sellerInfo = IMEIOwnership.SellerInfo(sellerNonce, sellerSig);

        bytes memory buyerMessage = abi.encodePacked(
            "tradeIMEI ", imeiHash, 
            " from ", seller, 
            " to ", buyer, 
            " price: ", Strings.toString(price),
            " (nonce: ", Strings.toString(buyerNonce), ")"
        );
        bytes memory buyerSig = makeSignature(buyerMessage, buyerPrivate);
        (uint8 v, bytes32 r, bytes32 s) = makePermitSignature(address(imeiCurrency), buyer, address(imeiOwnership), tradeInfo.price, block.timestamp + 1 minutes, buyerPrivate);
        IMEIOwnership.BuyerInfo memory buyerInfo = IMEIOwnership.BuyerInfo(buyerNonce, buyerSig, v, r, s, block.timestamp + 1 minutes);
        imeiOwnership.tradeIMEI(tradeInfo, sellerInfo, buyerInfo);
        assertEq(imeiOwnership.imeiHashToOwner(imeiHash), buyer);
        assertEq(imeiCurrency.balanceOf(buyer), 0);
    }

    function test_confirmTrade() public {
        test_tradeIMEI();
        buyerNonce = imeiOwnership.userNonce(buyer) + 1;
        bytes memory message = abi.encodePacked("confirmTrade ", imeiHash, " (nonce: ", Strings.toString(buyerNonce), ")");
        bytes memory sig = makeSignature(message, buyerPrivate);
        imeiOwnership.confirmTrade(imeiHash, buyerNonce, sig);
        assertEq(imeiCurrency.balanceOf(seller), 100000);
    }
}
