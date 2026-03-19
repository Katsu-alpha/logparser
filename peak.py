#!/usr/bin/python
#
#   peak.py
#
#   指定されたパラメータの min, max, avg を表示
#

import sys
import re
import argparse
import fileinput


parser = argparse.ArgumentParser(
    description="Calculate min/max/avg for the specified parameter.")
parser.add_argument('pattern', help="Parameter to parse", type=str)
parser.add_argument('files', help="Log files", type=str, nargs='+')
parser.add_argument('--excludelast', '-e', help='Exclude last n values', type=int, default=0)
args = parser.parse_args()

p = args.pattern
for fn in args.files:
    values = []
    with open(fn, encoding='mac_roman') as f:
        lines = f.readlines()

    for l in lines:
        if p not in l:
            continue
        m = re.search(r'\d+$', l)
        if not m:
            continue
        values.append(int(m.group(0)))

    if args.excludelast > 0:
        values = values[:-args.excludelast] if len(values) > args.excludelast else []

    if values:
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)
    else:
        min_val = 0
        max_val = 0
        avg_val = 0

    print(f'{fn:<25}: min={min_val:<5} max={max_val:<5} avg={avg_val}')

