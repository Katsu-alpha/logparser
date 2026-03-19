#!/usr/bin/python
#
#   radio-stats-retry.py
#
#   show ap debug radio-stats の以下のカウンタの差分から、リトライ率を計算
#   最初と最後の値を採用
#   - Tx Data Transmitted
#   - Tx Mgmt Transmitted Retried
#


import re
import argparse

end_pat = r' radio 1 advanced$'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=f"Calculate retry rates in 'show ap debug radio-stats'")
    parser.add_argument('infile', help="Input files(s) containing 'show ap debug radio-stats' output", type=str, nargs='+')
    parser.add_argument('--excludelast', '-e', help='Exclude last n values', type=int, default=0)
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
        txretr_values = []
        tx_values = []
        for l in lines:
            l = l.rstrip()
            if re.search(end_pat, l):
                break

            if l.startswith('Tx Data Transmitted Retried'):
                m = re.search(r'\d+', l)
                if m:
                    txretr_values.append(int(m.group(0)))
                continue
            if l.startswith('Tx Data Transmitted'):
                m = re.search(r'\d+', l)
                if m:
                    tx_values.append(int(m.group(0)))

        if args.excludelast > 0:
            txretr_values = txretr_values[:-args.excludelast] if len(txretr_values) > args.excludelast else []
            tx_values = tx_values[:-args.excludelast] if len(tx_values) > args.excludelast else []

        if txretr_values and tx_values:
            d_txretr = txretr_values[-1] - txretr_values[0]
            d_tx = tx_values[-1] - tx_values[0]
            if d_tx > 0:
                retry_rate = (d_txretr / d_tx) * 100
                print(f"{fn} {retry_rate:.2f}% ({d_txretr}/{d_tx})")
            else:
                print(f"{fn} N/A (tx delta is 0)")
        else:
            print(f"{fn} N/A (not enough data)")
        #break
