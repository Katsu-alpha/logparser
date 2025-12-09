#
#   radio-stats-drop.py
#
#   show ap debug radio-stats の以下のカウンタの差分から、ドロップ率を計算
#   最初と最後の値を採用
#   - Tx Frames Transmitted
#   - Tx Frames Dropped
#


import re
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=f"Calculate drop rates in 'show ap debug radio-stats'")
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
        s_txdrop = 0
        s_tx = 0
        for l in lines:
            if l.startswith('Tx Frames Dropped  '):
                m = re.search(r'\d+', l)
                if m:
                    txdrop = int(m.group(0)) 
                    e_txdrop = txdrop
                    if s_txdrop == 0:
                        s_txdrop = txdrop
                continue
            if l.startswith('Tx Frames Transmitted  '):
                m = re.search(r'\d+', l)
                if m:
                    tx = int(m.group(0)) 
                    e_tx = tx
                    if s_tx == 0:
                        s_tx = tx

        d_txdrop = e_txdrop - s_txdrop
        d_tx = e_tx - s_tx
        retry_rate = (d_txdrop/ d_tx) * 100
        print(f"{fn} {retry_rate:.2f}% ({d_txdrop}/{d_tx})")
        #break
