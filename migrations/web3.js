const Web3 = require('web3');
const web3 = new Web3('http://127.0.0.1:8545');

// Check the balance of the first account
web3.eth.getBalance('0x28814832b33F9add81BC8D302F863B5d87ddD49a')
  .then(balance => {
    console.log('Balance:', web3.utils.fromWei(balance, 'ether'), 'ETH');
  });

