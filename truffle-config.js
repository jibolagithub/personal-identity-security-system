require('dotenv').config();
const { MNEMONIC, PROJECT_ID } = process.env;
const HDWalletProvider = require('@truffle/hdwallet-provider');

module.exports = {
  networks: {
    ganache: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*",
    },
    development: {
      provider: () => new HDWalletProvider(MNEMONIC, `http://127.0.0.1:8545`),
      network_id: 5777, // Match any network id
      gas: 6721975, // Gas limit used for deploys
    },
    goerli: {
      provider: () => new HDWalletProvider(MNEMONIC, `https://goerli.infura.io/v3/${PROJECT_ID}`),
      network_id: 5,
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: true
    }
  },
  compilers: {
    solc: {
      version: "0.8.18",
      docker: true,
    }
  },
  db: {
    enabled: true,
    host: "127.0.0.1",
    adapter: {
      name: "indexeddb",
      settings: {
        directory: ".db"
      }
    }
  }
};

