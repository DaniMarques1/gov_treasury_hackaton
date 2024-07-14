Run main.py to gather transactions related to the address "0x245db945c485b68fdc429e4f7085a1761aa4d45d", which is the current treasury address.
This scripts will retrieve and treat data from 1st Jan 2024 to July 2024 and store them on a Mongodb database.
It takes a long time to retrieve all data because of the large number of blocks.
Result data will be s daily sum of WETH, and AXS by fee category.
Main goal here is to make a lightweight mongodb collection or json file for easy access.
