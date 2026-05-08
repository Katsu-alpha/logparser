#!/usr/bin/python
#
#   dif-client-table.py
#
#   Create a csv report of time series deltas for each client statistics
#
#   show ap debug client-table の出力を解析し、各クライアントの時系列のリトライ率、PHY rate, SNRをCSV形式で出力
#

import argparse
import sys
import re
from collections import defaultdict
from aos_parser import AOSParser

TXPKTS_THRESHOLD = 100      # Tx 1,000パケット未満の端末はリトライ率を表示しない


parser = argparse.ArgumentParser(description="Parse show ap debug client-table output and generate csv summary")
parser.add_argument('infiles', help="Input file(s)", type=str, nargs='+')
args = parser.parse_args()

p_txpkts = defaultdict(int)
p_txretr = defaultdict(int)
retry_rate = defaultdict(dict)
txrate = defaultdict(dict)
rxrate = defaultdict(dict)
snr = defaultdict(dict)
times = set()
cmd = "show ap debug client-table"
buf = None
macs = set()

dic_txpkts = defaultdict(dict)
dic_txretr = defaultdict(dict)
dic_txpkts_d = defaultdict(dict)
dic_txretr_d = defaultdict(dict)

for fn in args.infiles:
    f = open(fn, 'r', encoding='utf-8')
    try:
        lines = f.readlines()
    except UnicodeDecodeError:
        f = open(fn, 'r', encoding='macroman')
        lines = f.readlines()

    in_cont = False
    tim = p_tim = ""
    for l in lines:

        if in_cont:
            if l.startswith('Num '):    # end of table
                in_cont = False
                if not tim:
                    continue

                buf.append(l)
                # print("".join(buf))
                aos = AOSParser("".join(buf), [cmd])
                tbl = aos.get_table(cmd)
                if tbl is None:
                    continue

                times.add(tim)

                for r in tbl[1:]:
                    mac = r[0]
                    if not re.match(r"[a-f0-9:]{17}$", mac):
                        continue
                    macs.add(mac)
                    txpkts = int(r[9])
                    txretr = int(r[12])
                    _txrate = int(r[13])
                    _rxrate = int(r[14])
                    _snr = int(r[16])

                    txpkts_d = txpkts - p_txpkts[mac]
                    txretr_d = txretr - p_txretr[mac]
                    if txpkts_d < 0 or txretr_d < 0:
                        # counter wrap
                        txpkts_d = txpkts
                        txretr_d = txretr
                    p_txpkts[mac] = txpkts
                    p_txretr[mac] = txretr
                    rr = f"{(txretr_d / txpkts_d * 100):.1f}" if txpkts_d >= TXPKTS_THRESHOLD else ""
                    retry_rate[mac][tim] = rr
                    txrate[mac][tim] = _txrate
                    rxrate[mac][tim] = _rxrate
                    snr[mac][tim] = _snr
                    #
                    dic_txpkts[mac][tim] = txpkts
                    dic_txretr[mac][tim] = txretr
                    dic_txpkts_d[mac][tim] = txpkts_d
                    dic_txretr_d[mac][tim] = txretr_d

            else:
                buf.append(l)
                continue


        if l.startswith('TIME='):
            tim = l[5:].strip()
            continue
        elif l.startswith('Current Time'):
            m = re.search(r" (\d\d:\d\d:\d\d)$", l)
            if m:
                tim = m.group(1)
                continue
        elif l.startswith('Client Table'):
            # if tim[:5] == p_tim[:5]:
            if tim == p_tim:
                continue
            # new minute
            p_tim = tim
            in_cont = True
            buf = [cmd+"\n", l]
            continue



#
#   Generate summary in CSV format
#

macs = sorted(macs)
# 1st header: MAC addresses
buf = ","
for m in macs:
    buf += f'"{m}",,,,'
print(buf[:-1])   # remove last comma
# 2nd header
buf = "Time,"
for m in macs:
    buf += f'"Retry rate","Tx rate","Rx rate","SNR",'
print(buf[:-1])   # remove last comma


for t in sorted(times):
    buf = f"{t},"
    for m in macs:
        rr = retry_rate[m].get(t, "-")
        if rr != "-" and rr != "":
            # rr = rr + "%" + f" {dic_txretr[m][t]}(+{dic_txretr_d[m][t]}) / {dic_txpkts[m][t]}(+{dic_txpkts_d[m][t]})"
            rr = rr + "%" + f" ({dic_txretr_d[m][t]} / {dic_txpkts_d[m][t]})"
        txr = txrate[m].get(t, "-")
        rxr = rxrate[m].get(t, "-")
        s = snr[m].get(t, "-")
        buf += f'"{rr}",{txr},{rxr},{s},'
    print(buf[:-1])   # remove last comma


sys.exit(0)
