import pysrt
import os
import argparse
from datetime import datetime, date, timedelta
from smb.SMBConnection import SMBConnection
from datetime import date
# ------ Main ------- #

parser = argparse.ArgumentParser(description="Regex-based transcripts tag cleaner")
parser.add_argument("--user", type=str, help="LDAP user to connect to smb",
                        required=True)
parser.add_argument("--password", type=str, help="Password for LDAP user",
                        required=True)
parser.add_argument("--machine_name", type=str, help="Local machine name",
                        required=True)
parser.add_argument("--server_name", type=str, help="Remote name server",
                        required=True)
parser.add_argument("--server_ip", type=str, help="Ip of the remote server",
                        required=True)
parser.add_argument("--domain_name", type=str, help="Remote domain name",
                        required=True)
parser.add_argument("--share_path", type=str, help="Name of the main share path on server",
                        required=True)
parser.add_argument("--audio_folder", type=str, help="Name of the folder where audios are",
                        required=True)
parser.add_argument("--report", type=str, help="Set yes if reporte needed",
                        required=False)

args = parser.parse_args()

userID = args.user
password = args.password
client_machine_name = args.machine_name
server_name = args.server_name
server_ip = args.server_ip
domain_name = args.domain_name
temp_file = "temp.srt"

conn = SMBConnection(userID, password, client_machine_name, server_name, domain=domain_name, use_ntlm_v2=True,
                     is_direct_tcp=True)

conn.connect(server_ip, 445)

shares = conn.listShares()
filelist = conn.listPath(args.share_path, "/"+args.audio_folder)

total_times = []
for file in filelist:
    if file.filename.endswith(".srt"):
        file_obj = open(temp_file, "wb")
        conn.retrieveFile(args.share_path, '/'+args.audio_folder+'/'+file.filename, file_obj)
        file_obj.close()
        subs = pysrt.open(temp_file)
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

        print("Total time for ", file.filename,str(total_per_file))
        total_times.append(total_per_file)
        os.remove(temp_file)
    else:
        print("Not a valid srt file")

total = timedelta(0)
for i in range(len(total_times)):
    total  = total + total_times[i]

today = date.today()
print("Total files:", len(total_times))
print("Total time for",today,":",str(total))

if args.report == 'yes':
    f = open("report.txt", "w")
    f.write("Total files:"+ str(len(total_times))+"\n")
    f.write("Total time:"+str(total))
    f.close()
    with open("report.txt", 'rb') as file:
        conn.storeFile(args.share_path, '/Reportes/'+str(today)+"-"+args.audio_folder+'.txt', file)
    os.remove("report.txt")

conn.close()
