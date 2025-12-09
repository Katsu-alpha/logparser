#!/usr/bin/python
#
#   peak.py
#
#   指定されたパラメータの min, max, avg を表示
#

import sys
import re

import fileinput

if len(sys.argv) < 2:
    print("Usage: peak.py <param> <input-fil(s)>")
    sys.exit(1)

p = sys.argv[1]
for fn in sys.argv[2:]:
    min_val = 0xFFFFFFFF
    max_val = 0
    sum_val = 0
    num = 0
    with open(fn, encoding='utf-8') as f:
        lines = f.readlines()

    for l in lines:
        if p not in l:
            continue
        m = re.search(r'\d+$', l)
        if not m:
            continue

        num += 1
        val = int(m.group(0))
        sum_val += val
        min_val = min(min_val, val)
        max_val = max(max_val, val)

    print(f'{fn:<25}: min={min_val:<5} max={max_val:<5} avg={sum_val / num if num > 0 else 0}')

