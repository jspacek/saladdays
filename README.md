Proxy distribution simulator that compares an adaptive proxy distribution scheme to uniform random and power of d choice strategies. The adaptive proxy distribution "sandwiches" between bounds to minimize the amount of collateral damage of honest proxies.

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
