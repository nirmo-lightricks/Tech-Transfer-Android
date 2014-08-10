# chinese
# start = 0x5000
# finish = 0x62ff

# ethiopic
start = 0x1200
finish = 0x137f

current = start
while current <= finish:
    print unichr(current).encode("utf-8")
    current += 1
