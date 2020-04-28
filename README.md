Proxy distribution simulator that compares an adaptive proxy distribution scheme to 1) uniform random, 2) power of 2 choice strategies, and 3) Tor's `bridgedb` bridge distributor.

## SETUP

### Python
Tested on python 3.7.3

Additional libraries needed: `simpy`, `matplotlib`, `pandas`

## SIMULATION

Run `python simulation/run.py`

This runs the proxy needle algorithm and the 3 comparison algorithms.

## GENERATE ANALYSES

Run `python analysis/collateral_damage.py`
