#
#   radio-stats-bcmc.py
#
#   show ap debug radio-stats の以下のカウンタの差分から、BC/MC の airtime 使用比を表示
#   ファイル中の最初と最後のカウンタの差分をとる
#   - Tx Time Data Transmitted
#   - Tx Time BC/MC Data
#


import re
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=f"Calculate BC/MC rates in 'show ap debug radio-stats'")
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
        s_txtime = 0
        s_txbcmc = 0
        for l in lines:
            if l.startswith('Tx Time Data Transmitted'):
                m = re.search(r'\d+', l)
                txtime = int(m.group(0))
                if s_txtime == 0:
                    s_txtime = txtime
                continue
            if l.startswith('Tx Time BC/MC Data'):
                m = re.search(r'\d+', l)
                txbcmc = int(m.group(0))
                if s_txbcmc == 0:
                    s_txbcmc = txbcmc

        d_txtime = txtime - s_txtime
        d_txbcmc = txbcmc - s_txbcmc
        bcmc_rate = (d_txbcmc/ d_txtime) * 100
        print(f"{fn} {bcmc_rate:.2f}% ({d_txbcmc}/{d_txtime})")

