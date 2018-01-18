# Discovering arbitrage between different exchanges

The cryptocurrency market poses several opportunities to exploit arbitrages. While statistical arbitrage in the stock market is applied to various equities based on classic cointegration-based pairs trading strategy, the same concept can be applied to a crypto-currency that shares different closing prices in two different exchanges. This simple code serves to show how this opportunity can be taken advantage of. 

## Getting Started

Jupyter Notebook through the installation of Anaconda.

### Prerequisites

The code is carried out on Jupyter Notebook using Python 3.6. Most libraries imported in this code comes together with Anaconda.

### Break down of code

1. We first develop an API connection with Cryptocompare using Python package, Beautiful Soup, to extract the necessary information on Ether sold over different exchanges. 
2. Retrieve prices & volumes (traded in the last 24 hours) of ETH in different exchanges
3. Price Time-series of ETH in the different exchanges
4. Measure the average difference & standard deviation
5. Identify 2 exchanges with greatest average difference in prices & least standard deviation
6. Backtesting algo trading using statistical arbitrage for ETH/USD

### Assumptions made
1. After the current trade, a new one is opened immediately at the same prices;
2. There is no slipage assumed;
3. The short selling is available on both markets;
4. There is no commission fee structure incorporated into trades;
5. The margin calls are ignored.
