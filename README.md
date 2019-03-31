Proxy distribution simulator that compares an adaptive proxy distribution scheme to uniform random, power of 2 choice strategies, and Tor's `bridgedb` bridge distributor.

## SETUP

### Docker

build: `docker build --tag sim1 .`

verify image: `docker images`

ssh to container: `docker run -it --entrypoint=/bin/bash sim1:latest`

### Python
Use python3

`pip install simpy`

`pip install matplotlib`

`pip install pandas`


## RUN SIMULATION

In root directory: `python simulation/run.py`

## GENERATE ANALYSES

In root directory: `python analysis/collateral_damage.py`
