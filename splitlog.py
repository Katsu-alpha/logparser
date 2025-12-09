#!/usr/bin/python
#
#   splitlog.py
#
#   指定されたログファイルを分割し、コマンド名ごとに保存
#

import sys
import re
import os

re_prompt = re.compile(r'\([\w\) \[\]\*-]+#')
re_time = re.compile(r'Tue Nov 25 (\d\d:\d\d:\d\d)')        # <<<<<<<<<< CHANGE THIS!!!!
fn_fix = str.maketrans(r' /\?%*:|\"<>.', "_____________")

if len(sys.argv) < 2:
    print("Usage: splitlog.py <filename>...")
    exit(1)

for fn in sys.argv[1:]:
    print(f"Processing {fn}")
    f = open(fn, 'r', encoding='utf-8')
    try:
        lines = f.readlines()
    except UnicodeDecodeError:
        f = open(fn, 'r', encoding='macroman')
        lines = f.readlines()

    buf = []
    cmd2 = ""
    cmdfn = None
    tim_last = ""
    for lno, l in enumerate(lines,1):
        l = l.rstrip()
        if cmd2 == 'show clock' and (m := re_time.search(l)):
            tim = m.group(1)
            if tim > tim_last:
                tim_last = tim
        if m := re_prompt.match(l):
            # write previous command output if any
            if len(buf) > 0 and cmdfn is not None:
                with open(cmdfn, 'a', encoding='utf-8') as out:
                    out.write(f"TIME={tim_last}\nCOMMAND={cmd2}\n")
                    out.write("\n".join(buf) + "\n")
                buf = []
                cmdfn = None


            cmd = l[m.end():].strip()
            if not cmd.startswith('show '):
                continue

            # found new show command
            tmp = []
            for c in cmd:
                if c == '\x08':  # backspace
                    if len(tmp) > 0:
                        tmp.pop()
                else:
                    tmp.append(c)
            cmd2 = ''.join(tmp)
            if not cmd2.startswith('show '):
                print(f"{lno:8}: wrong command - '{cmd2}'")
                continue
            # print(f"{lno:8}: {cmd2}")
            buf = []
            cmdfn = f"{cmd2.translate(fn_fix)}.log"
        else:
            buf.append(l)

    if len(buf) > 0 and cmdfn is not None:
        with open(cmdfn, 'a', encoding='utf-8') as out:
            out.write(f"TIME={tim_last}\nCOMMAND={cmd2}\n")
            out.write("\n".join(buf) + "\n")
