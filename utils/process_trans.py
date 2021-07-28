import json
import argparse
from docx import Document

parser = argparse.ArgumentParser(description="Regex-based transcripts tag cleaner")
parser.add_argument("--input", type=str, help="path to json to transform",
                        required=True)
parser.add_argument("--output", type=str, help="path to save .doc",
                        required=True)
args = parser.parse_args()

input = args.input
output = args.output

document = Document()
with open(input) as f:
  data = json.load(f)

for element in data:
    element.pop('start', None)
    element.pop('end', None)


outF = ''

print(len(data))
count = 0
for row in data:
    count = count + 1
    if(count == 6):
        outF = outF + ("\n")
        count = 0
    else:
        outF = outF + row['transcript'] + ' '

document.add_paragraph(outF)
document.save(output)