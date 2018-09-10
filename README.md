# moneyMaker
This leverages the Interactive Brokers API and `ib_insync` python wrapper to return a single option contract.

# Hi
# Forked
# Get Option
`getOption.py` features a function to return a single option contract based on provided parameters. 
In order to select your contract, users must provide an ib object, `ticker`, `strike`, and some sort of expiry date.
Expiry dates can either be represented with `<int>` parameters `year`, `month`, and `day` or `date`. Specifications on the formats of these variables are provided in the file.
Optional parameters include `exchange`, `currency`, and `optType` which default to `'SMART'`, `'USD'`, and `'C'` respectively.
An example program is included in the file.


## Getting Started

Create an Interactive Brokers account at https://gdcdyn.interactivebrokers.com/ with options trading capabilities. Go through the installation process. Before running `getOption.py`, first open and run IB Gateway.



### Installing (for Drew when he forgets)

Intall all the requirements:

```
moneyMaker repository
Python 3.6
ib_insync (and its requirements from https://github.com/erdewit/ib_insync)
```