# Accounts

Currently the project supports two different platforms to place trades.

## Supported Platforms

### Metatrader 5
Metatrader 5 is a popular trading platform that allows you to trade Forex, stocks, and commodities.
It is widely used by traders around the world and offers a range of features and tools to help you analyze the market
and make informed trading decisions.

## Storing Secrets on AWS

1. Login to your AWS Account and go to the Secrets Manager.<br/>
<img src="../../../images/secrets_manager_search_bar_aws_console.png" title="AWS Secretsmanager Link" width="400"/>

2. Click on the "Store a new secret" button.<br/>

3. Select "Other type of secrets".<br/>
   4. Select "Plaintext".<br/>
      1. Metatrader 5 (Paste and adjust the following JSON):
           ```json
           {
                "MT5_USER_NAME": "<YOUR_MT5_USER_NAME>",
                "MT5_PASSWORD": "<YOUR_MT5_PASSWORD>",
                "MT5_SERVER": "<YOUR_MT5_SERVER>"
           }
           ```
           ```
4. Click on "Next".<br/>
5. Enter a name for the secret. The name should be unique and descriptive.<br/>
   1. For Metatrader 5, use the following format: `mt5/<YOUR_MT5_USER_NAME>`.
6. Click on "Next" until you can store the secret.<br/>
