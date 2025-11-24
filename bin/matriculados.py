#!/usr/bin/python3

import re

with open("sar.txt") as fp:

    reading = False

    for l in fp:

        s = l.split()

        if len(s) == 0:

            continue

        m = re.match("[\d]{3,5}", s[0])

        if (s[0] != "TOTAL") and (s[1] != "DO") and (m is None):

            continue

        if m is not None:

            if reading:

                print("{0:4s}\t{1:3s}\t{2:20s}\t{3:4s}\t{4:2s}".format(c,t,n,f,sm))

                reading = False

            reading = True

            c = s[0]

            t = s[1]

            n = s[2]

            sm = s[-5]

            if (sm == 'A') or (sm == 'S1') or (sm == 'S2'):

                sm = s[-6]

            i = 3

            while s[i] != "T" and s[i] != "P" and s[i] != "T-P" and s[i] != "TP":

                n += " " + s[i]

                i += 1

        if s[0] == "TOTAL" and s[1] == "DO":

            f = s[6]
