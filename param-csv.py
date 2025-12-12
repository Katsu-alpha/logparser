#!/usr/bin/python
#
#   param-csv.py
#
#   指定されたパラメータを、csv 形式で出力
#


import sys
import re
import argparse

end_pat = r' radio 1 advanced$'

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("param-csv.py <param> <file(s)>")
        sys.exit(0)

    param = sys.argv[1]
    files = sys.argv[2:]
    #
    #   parse radio stats
    #
    for fn in files:
        try:
            f = open(fn, encoding='utf-8')
            lines = f.readlines()
        except UnicodeDecodeError as e:
            f = open(fn, encoding='mac_roman')
            lines = f.readlines()
        f.close()

        times = []
        vals = []
        for l in lines:
            if l.startswith('Output Time:'):
                tst = l[13:].rstrip()
                continue
            if not re.search(param, l):
                continue

            l = l.rstrip()
            m = re.search(r'\d+$', l)
            if not m:
                continue

            val = m.group(0)
            times.append(tst)
            vals.append(val)

        print(f'{fn:<25}' + ','.join(times))
        print(f'{fn:<25}' + ','.join(vals))
