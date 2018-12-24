pragma solidity ^0.4.25;

contract BaseContract {

    address owner;

    uint256 bid;
    mapping (address => uint) bidders_map;
    address[] all_bidders;
    mapping (address => uint) winners_prize_map;
    bool is_open;

    modifier onlyOwner {
        if (msg.sender != owner) {
            revert();
        }
        _;
    }

    constructor() public payable {
        owner=msg.sender;
        bid = 0 ether;
        is_open = true;
    }

    function getOwner() public view returns (address){
        return owner;
    }

    function add_bid() public payable returns(bool success){

        require(is_open == true, 'Sorry bidding is closed');
        require(bidders_map[msg.sender] != 1, 'You have already placed the bid');
        require(msg.value == 0.1 ether, "Only 0.1 ether is allowed for placing bid");

        bidders_map[msg.sender] = 1;
        all_bidders.push(msg.sender);

        bid += msg.value;

        return true;
    }

    function total_bids() public view returns(uint, uint){
        return(bid, all_bidders.length);
    }

    function add_winners(address[] _winners) public onlyOwner{
        uint256 prize_per_winner = bid/_winners.length;

        is_open = false;

        for(uint i=0; i<_winners.length; i++){
            require(bidders_map[_winners[i]] > 0, "unrecognized bidder address");
            winners_prize_map[_winners[i]] = prize_per_winner;
        }

    }

    function claim_won_bid() public {
        require(winners_prize_map[msg.sender] > 0, "Invalid request");
        msg.sender.transfer(winners_prize_map[msg.sender]);
        bid -= winners_prize_map[msg.sender];
        delete winners_prize_map[msg.sender];
    }

}


contract BitCoin is BaseContract {
}


contract BitCoinCash is BaseContract {
}


contract Dogecoin is BaseContract {
}


contract Ethereum is BaseContract {
}


contract LiteCoin is BaseContract {
}
