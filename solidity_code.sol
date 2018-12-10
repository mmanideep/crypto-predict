pragma solidity ^0.4.20;

contract BaseContract {

    address owner;

    uint256 bid;

    mapping (address => uint) bidders_map;
    address[] all_bidders;

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

        require(bidders_map[msg.sender] != 1, 'You have already placed the bid');

        bidders_map[msg.sender] = 1;
        all_bidders.push(msg.sender);

        bid += 0.1 ether;

        return true;
    }

    function total_bids() public view returns(uint, uint){
        return(bid, all_bidders.length);
    }

    function distribute_bid(address[] _winners) public onlyOwner{

        for(uint i = 0; i < _winners.length; i++) {

            require(bidders_map[_winners[i]] > 0);

            _winners[i].transfer(bid/_winners.length);
        }

        for(i=0; i<all_bidders.length; i++){
            if(bidders_map[all_bidders[i]] > 0){
                delete bidders_map[all_bidders[i]];
            }
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
