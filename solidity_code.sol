pragma solidity^0.4.20;

contract BaseUserAuth {

    address owner;

    bytes32 id;

    modifier onlyOwner {
        if (msg.sender != owner) {
            revert();
        }
        _;
    }

    constructor() public {
        owner=msg.sender;
    }

    function setId(bytes32 _id) ownerOnly public{
        id = _id;
    }

    function getId(bytes32 _id) ownerOnly public{
        return id;
    }

    function getOwner() public returns (address){
        return owner;
    }

}
