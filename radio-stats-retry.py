#!/usr/bin/python
#
#   radio-stats-retry.py
#
#   show ap debug radio-stats の以下のカウンタの差分から、リトライ率を系sン
#   - Tx Data Transmitted
#   - Tx Data Transmitted Retried
#


import re
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=f"Calculate retry rates in 'show ap debug radio-stats'")
    parser.add_argument('infile', help="Input files(s) containing 'show ap debug radio-stats' output", type=str, nargs='+')
    args = parser.parse_args()

    #
    #   parse radio stats
    #
    for fn in args.infile:
        try:
            f = open(fn, encoding='utf-8')
            lines = f.readlines()
        except UnicodeDecodeError as e:
            f = open(fn, encoding='mac_roman')
            lines = f.readlines()
        f.close()
        pre_txretr = 0
        pre_tx = 0
        for l in lines:
            if l.startswith('Tx Data Transmitted Retried'):
                m = re.search(r'\d+', l)
                txretr = int(m.group(0)) if m else None
                continue
            if l.startswith('Tx Data Transmitted'):
                m = re.search(r'\d+', l)
                tx = int(m.group(0)) if m else None

                if tx is not None and txretr is not None and tx > 0:
                    if pre_txretr == 0:
                        pre_txretr = txretr
                        pre_tx = tx
                        continue
                    d_txretr = txretr - pre_txretr
                    d_tx = tx - pre_tx
                    pre_txretr = txretr
                    pre_tx = tx
                    retry_rate = (d_txretr/ d_tx) * 100 if d_tx > 0 else 0
                    print(f"{fn} {retry_rate:.2f}% ({d_txretr}/{d_tx})")
                continue
