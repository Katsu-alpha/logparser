#!/usr/bin/python
#
#   dif-radio-stat.py
#
#   Create a csv report of time series deltas for radio statistics
#

import sys
import re
from collections import defaultdict

stats = [
    # 'Total Radio Resets',
    'Tx Frames Dropped',
    # 'Tx Frames Transmitted',
    'Tx Unicast Data Frames',
    'Tx Data Transmitted Retried',
    'Channel Busy 4s'
]

pat = "^(" + "|".join(stats) + ")"
re_stat = re.compile(pat)

if len(sys.argv) < 2:
    print("Usage: splitlog.py <filename>...")
    exit(1)

fn = sys.argv[1]
f = open(fn, 'r', encoding='utf-8')
try:
    lines = f.readlines()
except UnicodeDecodeError:
    f = open(fn, 'r', encoding='macroman')
    lines = f.readlines()

stats = defaultdict(int)
values = defaultdict(dict)
deltas = defaultdict(dict)
times = set()
tim = None

for l in lines:
    if l.startswith('TIME='):
        tim = l[5:].strip()
        continue
    if m := re_stat.match(l):
        param = m.group(1)
        try:
            val = int(l[m.end():].strip())
        except ValueError:
            continue
        delta = val - stats[param]
        stats[param] = val
        if tim:
            times.add(tim)
            values[param][tim] = val
            deltas[param][tim] = delta

print("Time,Tx Unicast Data Frames,delta,Retry Frames,delta,Tx Dropped,delta,Ch Util(%),Retry Rate(%),Drop Rate(%)")
for t in sorted(times):
    chbusy = values['Channel Busy 4s'][t]
    txframes = values['Tx Unicast Data Frames'][t]
    txframes_delta = deltas['Tx Unicast Data Frames'][t]
    retry = values['Tx Data Transmitted Retried'][t]
    retry_delta = deltas['Tx Data Transmitted Retried'][t]
    dropped = values['Tx Frames Dropped'][t]
    dropped_delta = deltas['Tx Frames Dropped'][t]
    retry_rate = f"{(retry_delta / txframes_delta * 100):.1f}" if txframes_delta > 0 else ""
    drop_rate = f"{(dropped_delta / txframes_delta * 100):.2f}" if txframes_delta > 0 else ""
    print(f'{t},{txframes},{txframes_delta},{retry},{retry_delta},{dropped},{dropped_delta},{chbusy},"{retry_rate}","{drop_rate}"')
