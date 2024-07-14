Run main.py to gather transactions related to the address "0x245db945c485b68fdc429e4f7085a1761aa4d45d" and address "0xa99cacd1427f493a95b585a5c7989a08c86a616b", which is the current treasury and the old treasury addresses, respectively.
This process will retrieve and treat data from 29th March 2022 to 31st December 2023, and store them on a Mongodb database.
It takes a long time to retrieve all data because of the large number of blocks.
Result data will be a daily sum of WETH since the acknowledgment of the bridge hack.
Main goal here is to make a lightweight mongodb collection or json file for easy access.