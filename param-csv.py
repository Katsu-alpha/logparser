#!/usr/bin/python
#
#   param-csv.py
#
#   指定されたパラメータを、csv 形式で出力
#


import sys
import re
import argparse
from datetime import datetime, timedelta

end_pat = r' radio-stats 1$'

def utc2sgt(utcts):
    #
    #   UTC -> SGT
    #
    m = re.match(r'(\d{4})[/-](\d+)[/-](\d+) (\d+):(\d{2}):(\d{2})', utcts)
    if not m:
        return utcts

    dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                  int(m.group(4)), int(m.group(5)), int(m.group(6)))
    dt += timedelta(hours=8)
    return dt.strftime('%Y/%m/%d %H:%M:%S')

def roundtime(tstr):
    #
    #   時刻を 5 分単位に丸める
    #
    m = re.match(r'(\d+):(\d{2})', tstr)
    if not m:
        return tstr
    hr = int(m.group(1))
    mn = int(m.group(2))
    mn = (mn + 2) // 5 * 5
    if mn >= 60:
        hr += 1
        mn = 0
    return f'{hr}:{mn:02}'

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("param-csv.py <param> <file(s)>")
        sys.exit(0)

    param = sys.argv[1]
    files = sys.argv[2:]
    tst_disp = False
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
            if re.search(end_pat, l):
                break
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
            times.append('"' + utc2sgt(tst)[11:16]+ '"')
            vals.append(val)

        if not tst_disp:
            tst_disp = True
            print(f'{fn[:-4]},' + ','.join(times))
        print(f'{fn[:-4]},' + ','.join(vals))
