# dapp-monitor-besu

#### Set up Chainlens-Free

```
git clone https://github.com/web3labs/chainlens-free.git
cd chainlens-free
```

In order to start Chainlens you need to run the following command:

`NODE_ENDPOINT=http://besu-node:8545 PORT=26000 docker-compose -f docker-compose.yml -f chainlens-extensions/docker-compose-besu.yml up`

ID Dashboard 16455