#!/usr/bin/env python3

import os
import re

srcdir = os.path.dirname(__file__)
outdir = "."

module = "bxjakyureki"

def gregorian_to_jdn(y, m, d):
    return int((1461 * (y + 4800 + int((m - 14)/12)))/4) + int((367 * (m - 2 - 12 * (int((m - 14)/12))))/12) - int((3 * (int((y + 4900 + int((m - 14)/12))/100)))/4) + d - 32075

def julian_to_jdn(y, m, d):
    return 367 * y - int((7 * (y + 5001 + int((m - 9)/7)))/4) + int((275 * m)/9) + d + 1729777

def western_to_jdn(y, m, d):
    if y < 1582 or (y == 1582 and (m < 10 or (m == 10 and d < 15))):
        return julian_to_jdn(y, m, d)
    else:
        return gregorian_to_jdn(y, m, d)

kyureki_end_jdn = western_to_jdn(1873, 1, 1) # In Japan, the Gregorian calendar was used from 1873.

def western_from_jdn(J):
    y = 4716
    j = 1401
    m = 2
    n = 12
    r = 4
    p = 1461
    v = 3
    u = 5
    s = 153
    w = 2
    B = 274277
    C = -38
    if J < 2299161:
        f = J + j
    else:
        f = J + j + (((4 * J + B) // 146097) * 3) // 4 + C
    e = r * f + v
    g = (e % p) // r
    h = u * g + w
    D = (h % s) // u + 1
    M = (h // s + m) % n + 1
    Y = (e // p) - y + (n + m - M) // n
    return (Y, M, D)

def roughly_kyureki_year(jdn):
    return round((jdn - 55 + 183) * 10000 / 3652422) - 4713

def make_kyureki(in_path, out_path):
    re_kyureki = re.compile(r"^(\d+)/(\d+)/(\d+)\t.*?(?:元|\d+)年(閏|)(\d+)月01日\t(\d+)\t\S+\t\S+\t(大|小)\t[^\t]*\t[^\t]*\s*$", re.ASCII)

    data = {}
    last_year  = None
    last_jdn   = None

    # read db file
    with open(in_path, "r", encoding="utf8") as f:
        for line in f:
            m = re_kyureki.match(line)
            west_y = int(m.group(1))
            west_m = int(m.group(2))
            west_d = int(m.group(3))
            leap   = m.group(4) == "閏"
            month  = int(m.group(5))
            year   = int(m.group(6)) - 660
            daisho = m.group(7) == "大"

            jdn = western_to_jdn(west_y, west_m, west_d)
            if last_jdn is not None:
                days = jdn - last_jdn
                if days < 29 or days > 30:
                    print("Error: days", days, line)
                last_jdn = jdn

            if last_year is None or year != last_year:
                last_year = year
                data[year] = [year, jdn, None, [None, None, None, None, None, None, None, None, None, None, None, None] ]
            if leap:
                l = data[year][2]
                if l is not None:
                    print("Error: leap", l, line)
                data[year][2] = [month,daisho]
            else:
                m = data[year][3]
                if m[month-1] is not None:
                    print("Error: month", m, line)
                m = data[year][3][month-1] = daisho

    # write def file
    with open(out_path, "w", encoding="utf8") as f:

        k = min(data.keys())
        d = data[k]
        y = d[0]
        n = d[1]
        min_y = y
        min_n = n

        k = max(data.keys())
        d = data[k]
        y = d[0] + 1
        n = d[1]
        l = d[2]
        m = d[3]
        if l is not None:
            n += (30 if l[1] else 29)
        for md in m:
            n += (30 if md else 29)
        max_y = y
        max_n = n

        f.write(f"\\__{module}_gset_kyureki_data_range:nn {{ {min_n} }} {{ {min(max_n, kyureki_end_jdn)} }}\n")

        # dummy entry
        f.write(f"\\__{module}_gset_kyureki_data:nnnnn {{ {max_y} }} {{ {max_n} }} {{}} {{}} {{}}\n")

        for k in reversed(sorted(data.keys())):
            d = data[k]
            y = d[0]
            n = d[1]
            l = d[2]
            m = d[3]
            l = [0,False] if l is None else l
            lm = l[0]
            ld = "1" if l[1] else "0"
            m = "".join([("1" if m else "0") for m in m])
            f.write(f"\\__{module}_gset_kyureki_data:nnnnn {{ {y} }} {{ {n} }} {{ {lm:2} }} {{ {ld} }} {{ {m} }}\n")

            ry = roughly_kyureki_year(n)
            if y != ry:
                print(y, ry)

def to_hex_jis(s):
    def pairwise(i):
        a = iter(i)
        return zip(a, a)
    return ", ".join(["{:04X}".format((a * 0x100 + b) - 0x8080) for a, b in pairwise(s.encode("euc_jp"))])

def to_hex_unicode(s):
    return ", ".join(["{:04X}".format(ord(c)) for c in s])

def to_hex_utf8(s):
    return ", ".join(["{:02X}".format(b) for b in s.encode("utf8")])

def make_gengo(in_path, out_path):
    re_gengo = re.compile(r"^(\S+)\t(?:\S+)\t(?:.+)年(閏|)(\d+)月(\d+)日\t（(\d+)年(\d+)月(\d+)日）$", re.ASCII)

    data = []

    # read db file
    with open(in_path, "r", encoding="utf8") as f:
        f.readline()
        for line in f:
            m = re_gengo.match(line)
            gengo = m.group(1)
            uru   = m.group(2) == "閏"
            getsu = int(m.group(3))
            nichi = int(m.group(4))
            year  = int(m.group(5))
            month = int(m.group(6))
            day   = int(m.group(7))
            
            nen = year
            if getsu >= 11 and month <= 2:
                nen = year - 1
            elif getsu > month:
                print(line)

            data.append([gengo, nen, uru, getsu, nichi, year, month, day ])

    # write def file
    with open(out_path, "w", encoding="utf8") as f:
        for d in data:
            gengo = d[0]
            nen   = d[1]
            uru   = 1 if d[2] else 0
            getsu = d[3]
            nichi = d[4]
            gengo_jis = to_hex_jis(gengo)
            gengo_uni = to_hex_unicode(gengo)
            gengo_utf = to_hex_utf8(gengo)
            f.write(f"\\__{module}_gput_gengo_data:nnnnnnn {{ {nen} }} {{ {uru} }} {{ {getsu:2} }} {{ {nichi:2} }} {{ {gengo_jis} }} {{ {gengo_uni} }} {{ {gengo_utf} }}\n")

#    with open("test-gengo.tex", "w", encoding="utf8") as f:
#        for d in data:
#            year2  = d[5]
#            month2 = d[6]
#            day2   = d[7]
#            year1, month1, day1 = western_from_jdn(western_to_jdn(year2, month2, day2) - 1)
#            f.write(f"  \\TYPE {{ \\jakyureki {{ {year2:4} }} {{ {month2:2} }} {{ {day2:2} }} }}\n")
#            f.write(f"  \\TYPE {{ \\jakyureki {{ {year1:4} }} {{ {month1:2} }} {{ {day1:2} }} }}\n")

if __name__ == "__main__":
    make_kyureki(os.path.join(srcdir, "kyureki.tsv"), os.path.join(outdir, f"{module}-kyureki.def"))
    make_gengo(os.path.join(srcdir, "gengo.tsv"), os.path.join(outdir, f"{module}-gengo.def"))
