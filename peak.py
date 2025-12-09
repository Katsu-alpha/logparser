#
#   peak.py
#
#   指定されたカウンタの min, max, avg を表示
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
        pre_txtime = 0
        pre_txbcmc = 0
        txtime = None
        txbcmc = None
        for l in lines:
            if l.startswith('Tx Time Data Transmitted'):
                m = re.search(r'\d+', l)
                txtime = int(m.group(0)) if m else None
                continue
            if l.startswith('Tx Time BC/MC Data'):
                m = re.search(r'\d+', l)
                txbcmc = int(m.group(0)) if m else None

                if txbcmc is not None and txtime is not None and txbcmc > 0:
                    if pre_txtime == 0:
                        pre_txtime = txtime
                        pre_txbcmc = txbcmc
                        continue
                    d_txtime = txtime - pre_txtime
                    d_txbcmc = txbcmc - pre_txbcmc
                    pre_txtime = txtime
                    pre_txbcmc = txbcmc
                    bcmc_rate = (d_txbcmc/ d_txtime) * 100
                    print(f"{fn} {bcmc_rate:.2f}% ({d_txbcmc}/{d_txtime})")

                continue
