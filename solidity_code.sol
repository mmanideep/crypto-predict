pragma solidity ^0.4.20;

contract BaseContract {

    address owner;

    uint256 bid;

    event LogBid(address sender, uint amount);
    event LogClaim(address[] receivers, uint amount);

    modifier onlyOwner {
        if (msg.sender != owner) {
            revert();
        }
        _;
    }

    constructor() public {
        owner=msg.sender;
        bid = 0 ether;
    }

    function getOwner() public view returns (address){
        return owner;
    }

    function add_bid() public payable returns(bool success){
        bid += msg.value;
        return true;
    }

    function distribute_bid(address[] _winners) public onlyOwner{
        for(uint i = 0; i < _winners.length; i++) {
            _winners[i].transfer(bid/_winners.length);
        }
        emit LogClaim(_winners, bid/_winners.length);
        bid = 0 ether;
    }

}


contract BitCoin is BaseContract {
}


contract BitCoinCash is BaseContract {
}


contract Ripple is BaseContract {
}


contract Ethereum is BaseContract {
}


contract LiteCoin is BaseContract {
}
