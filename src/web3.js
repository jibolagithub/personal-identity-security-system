// Define ABI and bytecode of your smart contract
const contractABI = [...]; // ABI of your smart contract
const bytecode = '0x...'; // Compiled bytecode of your smart contract

// Create a contract object
const contract = new web3.eth.Contract(contractABI);

// Deploy the contract
contract.deploy({
    data: bytecode,
    arguments: [constructorArgs] // if your constructor takes arguments
})
.send({
    from: userAddress, // User's Metamask address
    gas: 1500000, // Gas limit
    gasPrice: '30000000000' // Gas price (wei)
})
.on('transactionHash', function(hash){
    // Transaction Hash
    console.log('Transaction hash:', hash);
})
.on('receipt', function(receipt){
    // Contract deployed successfully
    console.log('Contract deployed at:', receipt.contractAddress);
})
.on('error', function(error){
    // Deployment failed
    console.error('Deployment error:', error);
});

