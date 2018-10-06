### Setup
Use python3

- pip install simpy
- pip install matplotlib
- python simnormal.py

### Notes

If the blocking rate is too* close to the assignment rate, there won't be enough opportunity for the
assigned proxy list to build up before proxies are selected from the vulnerable list. Make sure there
is enough of a buffer set so that the proxies can accumulate before blocking. Default is 10 times as slow

* not sure what the threshold point is for this assignment rate yet

### TODO items

- further the analysis in all bounds and two choice
- add state in the agetwochoice file for normal, attack, recovery states
- figure out some rates of attack, and how to delay the attack in a tail fashion
- rate of attack should be conditioned on the ratio of attackers
- refuse proxy assignments when maximum load reached, default m/n
- make the choice of malicious clients configurable (currently uniform)

> My salad days, When I was green in judgment, cold in blood, To say as I said then! - Antony and Cleopatra
