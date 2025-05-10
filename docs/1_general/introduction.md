
# Introduction

## Disclaimer

Trading involves substantial risk and is not suitable for everyone. The information provided by this software is for educational and research purposes only. Past performance does not guarantee future results. You are solely responsible for any trades placed using this bot. Use it at your own risk. The developer assumes no liability for financial losses or damages resulting from the use of this tool.

## What is this?

This is a local trading bot that allows trading multiple accounts at the same time.
This project has been created to pass and trade prop firm challenges, as well as to trade live accounts.

## Why this?

Trading is a complex and risky activity, and it requires a lot of time and effort to be successful.
Computer programs help automate the process and make it easier to manage multiple accounts.
Additionally, they are helping to reduce the risk of human error and emotional decision-making.

## Requirements

* A Windows PC
  * Metatrader 5 is not supported on MacOS and Linux. A setup with `wine` has not been tested.
* An active AWS account
  * I use AWS to store the secrets for the accounts. Maybe I will add a local solution in the future.
* Polygon API key (optional)
  * I use Polygon to get the data for the strategies. You can use any other data provider, but you will have to modify the code.
* TradingView account (optional)
  * I use TradingView to get the signals for the strategies. You can use any other signal provider, but you will have to modify the code.
