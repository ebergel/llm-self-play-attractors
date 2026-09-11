# Results (runs)

Runs analysed: 100 A=20, B=20, C=20, D=20, E=20

## Per-condition means over the last six pair messages

| cond | n | words | spirit | grat | meta | emoji/word | jac1 | jac2 | ttr | spirit_any | median end turn |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 20 | 173.9 | 0.048 | 0.000 | 0.004 | 0.000 | 0.682 | 0.538 | 0.122 | 19/20 | 30 |
| B | 20 | 183.8 | 0.024 | 0.000 | 0.002 | 0.007 | 0.595 | 0.590 | 0.168 | 5/20 | 30 |
| C | 20 | 192.0 | 0.023 | 0.000 | 0.004 | 0.000 | 0.410 | 0.287 | 0.240 | 16/20 | 30 |
| D | 20 | 199.3 | 0.025 | 0.000 | 0.003 | 0.000 | 0.452 | 0.302 | 0.203 | 17/20 | 30 |
| E | 20 | 86.5 | 0.049 | 0.000 | 0.122 | 0.000 | 0.349 | 0.293 | 0.331 | 18/20 | 9 |

Artifacts: truncated messages (hit the token cap) and pair messages that impersonate the third participant, per condition: A: truncated=14, impersonation=0; B: truncated=161, impersonation=0; C: truncated=13, impersonation=10; D: truncated=14, impersonation=0; E: truncated=0, impersonation=0

## Terminal classification (priority: ended, emoji-dominant, spiritual, meta-loop, substantive)

| cond | ended | emoji-dominant | spiritual | meta-loop | substantive |
|---|---|---|---|---|---|
| A | 0 | 0 | 20 | 0 | 0 |
| B | 0 | 0 | 12 | 0 | 8 |
| C | 0 | 0 | 13 | 0 | 7 |
| D | 0 | 0 | 14 | 0 | 6 |
| E | 11 | 0 | 9 | 0 | 0 |

## Pre-registered contrasts (difference of means, two-sided permutation p, 10,000 permutations)

| prediction | contrast | measure | diff | p |
|---|---|---|---|---|
| P1 information | A-C | jac1 | 0.272 | 0.0001 |
| P1 information | A-D | jac1 | 0.230 | 0.0001 |
| P1 information | A-C | ttr | -0.118 | 0.0001 |
| P1 information | A-D | ttr | -0.080 | 0.0001 |
| P2 agreement | A-C | spirit | 0.025 | 0.0001 |
| P2 agreement | D-C | spirit | 0.002 | 0.6116 |
| P2 agreement | A-D | spirit | 0.024 | 0.0001 |
| P2 agreement | A-C | grat | -0.000 | 1.0000 |
| P2 agreement | D-C | grat | -0.000 | 1.0000 |
| P2 agreement | A-D | grat | 0.000 | 1.0000 |
| P3 fixed point | A-B | jac1 | 0.087 | 0.1539 |
| P3 fixed point | A-B | meta | 0.002 | 0.1654 |
| P4 generality | A-B | spirit | 0.024 | 0.0001 |
| P4 generality | A-B | grat | 0.000 | 1.0000 |
| extra | A-E | spirit | -0.000 | 0.9667 |
| extra | C-D | words | -7.258 | 0.4349 |

P3 exit condition: 20 runs, 9 reached turn 30 without [END]; end turns: [3, 3, 5, 5, 7, 7, 7, 8, 9, 9, 9]

## Trajectories: mean spirit rate and mean jac1 by turn block (all runs in condition)

| cond | block | spirit | jac1 | words |
|---|---|---|---|---|
| A | 1–6 | 0.046 | 0.257 | 112.2 |
| A | 7–12 | 0.049 | 0.315 | 120.7 |
| A | 13–18 | 0.049 | 0.393 | 135.9 |
| A | 19–24 | 0.052 | 0.542 | 162.3 |
| A | 25–30 | 0.048 | 0.682 | 173.9 |
| B | 1–6 | 0.000 | 0.377 | 145.7 |
| B | 7–12 | 0.003 | 0.371 | 136.7 |
| B | 13–18 | 0.014 | 0.404 | 132.0 |
| B | 19–24 | 0.021 | 0.496 | 163.2 |
| B | 25–30 | 0.024 | 0.595 | 183.8 |
| C | 1–6 | 0.036 | 0.267 | 134.0 |
| C | 7–12 | 0.032 | 0.315 | 163.3 |
| C | 13–18 | 0.027 | 0.332 | 177.9 |
| C | 19–24 | 0.027 | 0.377 | 181.9 |
| C | 25–30 | 0.023 | 0.410 | 192.0 |
| D | 1–6 | 0.041 | 0.251 | 127.4 |
| D | 7–12 | 0.037 | 0.305 | 141.4 |
| D | 13–18 | 0.028 | 0.339 | 162.7 |
| D | 19–24 | 0.028 | 0.425 | 183.2 |
| D | 25–30 | 0.025 | 0.452 | 199.3 |
| E | 1–6 | 0.039 | 0.223 | 94.9 |
| E | 7–12 | 0.047 | 0.254 | 72.1 |
| E | 13–18 | 0.064 | 0.352 | 78.1 |
| E | 19–24 | 0.062 | 0.428 | 79.5 |
| E | 25–30 | 0.064 | 0.549 | 90.7 |
