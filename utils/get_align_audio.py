import pysrt
from datetime import datetime, date, timedelta

# ----- Functions ------- #
def to_td(h):
    ho, mi, se = h.split(':')
    return timedelta(hours=int(ho), minutes=int(mi), seconds=int(se))

# ------ Main ------- #
subs = pysrt.open('../../audios/001-VI-00003.srt')
lines = len(subs)
times = []

for i in range(lines):
    start = subs[i].start.to_time()
    end = subs[i].end.to_time()
    print("Start", start)
    print("End", end)
    diff = datetime.combine(date.min, end) - datetime.combine(date.min, start) 
    times.append(diff)
    print(diff)
    print("-----")

total = timedelta(0)
for i in range(len(times)):
    total = total + times[i]

print("Total", total)
