// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/IMEIOwnership.sol";
import "../src/token.sol";

contract IMEIOwnershipTest is Test {
    IMEICurrency token;
    IMEIOwnership ownership;

    uint256 sellerPrivateKey = 0xA11CE;
    uint256 buyerPrivateKey = 0xB0B;
    address seller;
    address buyer;

    address contractOwner = address(1);
    bytes32 imeiHash;
    uint256 price = 1000;

    function setUp() public {
        // 서명자 주소 정의
        seller = vm.addr(sellerPrivateKey);
        buyer = vm.addr(buyerPrivateKey);

        // contractOwner로 배포 및 mint
        vm.startPrank(contractOwner);
        token = new IMEICurrency();
        ownership = new IMEIOwnership(address(token));
        token.mint(buyer, 2000);
        vm.stopPrank();

        imeiHash = keccak256(abi.encodePacked("IMEI123456789"));
    }

    function signAsBytes(uint256 privKey, bytes32 hash) internal pure returns (bytes memory) {
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(privKey, hash);
        return abi.encodePacked(r, s, v);
    }

    function getPermitDigest(
        IMEICurrency _token,
        address owner_,
        address spender,
        uint256 value,
        uint256 nonce,
        uint256 deadline
    ) public view returns (bytes32) {
        bytes32 DOMAIN_SEPARATOR = _token.DOMAIN_SEPARATOR();
        bytes32 structHash = keccak256(
            abi.encode(
                keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"),
                owner_,
                spender,
                value,
                nonce,
                deadline
            )
        );
        return keccak256(abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash));
    }

    // 1. 등록 테스트 함수
    function testRegisterIMEI() public {
        uint nonce = 1;
        bytes32 msgHash = MessageHashUtils.toEthSignedMessageHash(
            keccak256(abi.encodePacked("registerIMEI", seller, imeiHash, nonce))
        );
        bytes memory signature = signAsBytes(sellerPrivateKey, msgHash);

        vm.prank(contractOwner);
        ownership.registerIMEI(seller, imeiHash, nonce, signature);

        assertEq(ownership.getIMEIOwner(imeiHash), seller);
    }

    // 2. 조회 테스트 함수
    function testGetIMEIOwner() public {
        uint nonce = 1;
        bytes32 msgHash = MessageHashUtils.toEthSignedMessageHash(
            keccak256(abi.encodePacked("registerIMEI", seller, imeiHash, nonce))
        );
        bytes memory signature = signAsBytes(sellerPrivateKey, msgHash);

        vm.prank(contractOwner);
        ownership.registerIMEI(seller, imeiHash, nonce, signature);

        address owner = ownership.getIMEIOwner(imeiHash);
        assertEq(owner, seller);
    }

    // 3. 거래 테스트 함수
    function testTradeIMEI() public {
        // 1단계: 등록
        uint sellerNonce = 1;
        bytes32 registerHash = MessageHashUtils.toEthSignedMessageHash(
            keccak256(abi.encodePacked("registerIMEI", seller, imeiHash, sellerNonce))
        );
        bytes memory registerSig = signAsBytes(sellerPrivateKey, registerHash);
        vm.prank(contractOwner);
        ownership.registerIMEI(seller, imeiHash, sellerNonce, registerSig);

        // 2단계: 거래 서명 생성
        uint tradePrice = price;
        uint sellerTradeNonce = 2;
        uint buyerTradeNonce = 3;
        uint256 deadline = block.timestamp + 1 hours;

        bytes32 tradeHashSeller = MessageHashUtils.toEthSignedMessageHash(
            keccak256(abi.encodePacked("tradeIMEI", seller, buyer, imeiHash, tradePrice, sellerTradeNonce))
        );
        bytes memory sellerSignature = signAsBytes(sellerPrivateKey, tradeHashSeller);

        bytes32 tradeHashBuyer = MessageHashUtils.toEthSignedMessageHash(
            keccak256(abi.encodePacked("tradeIMEI", seller, buyer, imeiHash, tradePrice, buyerTradeNonce))
        );
        bytes memory buyerSignature = signAsBytes(buyerPrivateKey, tradeHashBuyer);

        // Permit 서명
        uint256 permitNonce = token.nonces(buyer);
        bytes32 permitDigest = getPermitDigest(token, buyer, address(ownership), tradePrice, permitNonce, deadline);
        (uint8 pv, bytes32 pr, bytes32 ps) = vm.sign(buyerPrivateKey, permitDigest);

        // 3단계: 거래 실행
        IMEIOwnership.TradeInfo memory tradeInfo = IMEIOwnership.TradeInfo(seller, buyer, imeiHash, tradePrice);
        IMEIOwnership.SellerInfo memory sellerInfo = IMEIOwnership.SellerInfo(sellerTradeNonce, sellerSignature);
        IMEIOwnership.BuyerInfo memory buyerInfo = IMEIOwnership.BuyerInfo(buyerTradeNonce, buyerSignature, pv, pr, ps, deadline);

        vm.prank(contractOwner); // 외부에서 거래를 initiate
        ownership.tradeIMEI(tradeInfo, sellerInfo, buyerInfo);

        // 4단계: 상태 확인
        assertEq(ownership.getIMEIOwner(imeiHash), buyer);
        assertEq(token.balanceOf(address(ownership)), price);
        assertEq(token.balanceOf(buyer), 2000 - price);
    }

    // 4. 확정 테스트 함수
    function testConfirmTrade() public {
        // 사전 조건: 거래까지 마친 상태를 복제
        testTradeIMEI();

        // 1단계: 서명 생성
        bytes32 confirmHash = MessageHashUtils.toEthSignedMessageHash(
            keccak256(abi.encodePacked("confirmTrade", imeiHash))
        );
        bytes memory confirmSig = signAsBytes(buyerPrivateKey, confirmHash);

        // 2단계: 거래 확정
        vm.prank(buyer);
        ownership.confirmTrade(imeiHash, confirmSig);

        // 3단계: 결과 확인
        assertEq(token.balanceOf(seller), price);
        assertEq(token.balanceOf(address(ownership)), 0);
    }

    function test_RevertWhen_QueryUnregisteredIMEIOwner() public {
        // 등록 안 한 상태에서 주소가 seller가 아니므로 assert 실패
        address owner = ownership.getIMEIOwner(imeiHash);
        assertEq(owner, address(0)); // address(0)과 같음->조회안됨성공
    }

    function test_RevertWhen_TransferUnregisteredIMEI() public {
        uint nonce = 1;
        bytes32 msgHash = MessageHashUtils.toEthSignedMessageHash(
            keccak256(abi.encodePacked("transferIMEI", seller, buyer, imeiHash, nonce))
        );
        bytes memory signature = signAsBytes(sellerPrivateKey, msgHash);

        vm.expectRevert("IMEI not found");
        vm.prank(buyer);
        ownership.transferIMEI(imeiHash, seller, buyer, nonce, signature);
    }

    function test_RevertWhen_TransferFromWrongOwner() public {
        uint nonce = 1;
        bytes32 regHash = MessageHashUtils.toEthSignedMessageHash(
            keccak256(abi.encodePacked("registerIMEI", seller, imeiHash, nonce))
        );
        bytes memory regSig = signAsBytes(sellerPrivateKey, regHash);
        vm.prank(contractOwner);
        ownership.registerIMEI(seller, imeiHash, nonce, regSig);

        uint wrongNonce = 2;
        bytes32 transferHash = MessageHashUtils.toEthSignedMessageHash(
            keccak256(abi.encodePacked("transferIMEI", buyer, seller, imeiHash, wrongNonce))
        );
        bytes memory wrongSig = signAsBytes(buyerPrivateKey, transferHash);

        vm.expectRevert("Not IMEI owner");
        vm.prank(seller);
        ownership.transferIMEI(imeiHash, buyer, seller, wrongNonce, wrongSig);
    }

    function test_RevertWhen_InsufficientBalance() public {
        // 등록
        uint nonce = 1;
        bytes32 regHash = MessageHashUtils.toEthSignedMessageHash(
            keccak256(abi.encodePacked("registerIMEI", seller, imeiHash, nonce))
        );
        bytes memory regSig = signAsBytes(sellerPrivateKey, regHash);
        vm.prank(contractOwner);
        ownership.registerIMEI(seller, imeiHash, nonce, regSig);

        uint overPrice = 3000;
        uint sellerTradeNonce = 2;
        uint buyerTradeNonce = 3;
        uint deadline = block.timestamp + 1 hours;

        bytes32 sellerHash = MessageHashUtils.toEthSignedMessageHash(
            keccak256(abi.encodePacked("tradeIMEI", seller, buyer, imeiHash, overPrice, sellerTradeNonce))
        );
        bytes memory sellerSig = signAsBytes(sellerPrivateKey, sellerHash);

        bytes32 buyerHash = MessageHashUtils.toEthSignedMessageHash(
            keccak256(abi.encodePacked("tradeIMEI", seller, buyer, imeiHash, overPrice, buyerTradeNonce))
        );
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(buyerPrivateKey, buyerHash);
        bytes memory buyerSig = abi.encodePacked(r, s, v);

        uint permitNonce = token.nonces(buyer);
        bytes32 permitDigest = getPermitDigest(token, buyer, address(ownership), overPrice, permitNonce, deadline);
        (uint8 pv, bytes32 pr, bytes32 ps) = vm.sign(buyerPrivateKey, permitDigest);

        IMEIOwnership.TradeInfo memory tradeInfo = IMEIOwnership.TradeInfo(seller, buyer, imeiHash, overPrice);
        IMEIOwnership.SellerInfo memory sellerInfo = IMEIOwnership.SellerInfo(sellerTradeNonce, sellerSig);
        IMEIOwnership.BuyerInfo memory buyerInfo = IMEIOwnership.BuyerInfo(buyerTradeNonce, buyerSig, pv, pr, ps, deadline);

        vm.expectRevert("Buyer lack of Balance");
        vm.prank(buyer);
        ownership.tradeIMEI(tradeInfo, sellerInfo, buyerInfo);
    }


}