// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Permit} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract IMEICurrency is ERC20, Ownable, ERC20Permit {
    constructor()
        ERC20("IMEICurrency", "IMCY")
        Ownable(msg.sender)
        ERC20Permit("IMEICurrency") {}

    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
}