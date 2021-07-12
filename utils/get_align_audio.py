import pysrt
import glob, os
from datetime import datetime, date, timedelta

# ------ Main ------- #

total_times = []
dir = "../../audios/"

for file in os.listdir(dir):
    if file.endswith(".srt"):
        subs = pysrt.open(os.path.join(dir, file))
        lines = len(subs)
        times_per_line = []
        #print("Subs for", file, ":", lines)
    
        for i in range(lines):
            start = subs[i].start.to_time()
            end = subs[i].end.to_time()
            #print("Start", start)
            #print("End", end)
            diff = datetime.combine(date.min, end) - datetime.combine(date.min, start) 
            times_per_line.append(diff)
            #print(diff)
            #print("-----")

        total_per_file = timedelta(0)
        for i in range(len(times_per_line)):
            total_per_file  = total_per_file + times_per_line[i]

        print("Total time for ", file,str(total_per_file))
    total_times.append(total_per_file)

total = timedelta(0)
for i in range(len(total_times)):
    total  = total + total_times[i]

print("Total time for all", str(total))


