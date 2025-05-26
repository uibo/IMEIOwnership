// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {IMEICurrency} from "../src/IMEICurrency.sol";
import {IMEIOwnership} from "../src/IMEIOwnership.sol";

contract IMEIOwnershipScript is Script {
    IMEICurrency imeiCurrency;
    IMEIOwnership imeiOwnership;

    function setUp() public {}

    function run() public {
        vm.startBroadcast();

        imeiCurrency = new IMEICurrency();
        imeiOwnership = new IMEIOwnership(address(imeiCurrency));

        vm.stopBroadcast();

        console.log("IMEICurrency: " , address(imeiCurrency));
        console.log("IMEIOwnership: " , address(imeiOwnership));
    }
}
