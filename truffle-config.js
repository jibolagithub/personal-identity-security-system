require('dotenv').config();
const { MNEMONIC, PROJECT_ID } = process.env;

const HDWalletProvider = require('@truffle/hdwallet-provider');

module.exports = {
  networks: {
    ganache: {
      host: "127.0.0.1",
      port: 7545,
      network_id: "5777",
    },
    goerli: {
      provider: () => new HDWalletProvider(MNEMONIC, `https://goerli.infura.io/v3/${PROJECT_ID}`),
      network_id: 5,
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: true
    },
    private: {
      provider: () => new HDWalletProvider(MNEMONIC, `https://network.io`),
      network_id: 2111,
      production: true
    }
  },
  compilers: {
    solc: {
      version: "0.8.18",
      docker: false,
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

