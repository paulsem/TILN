import xml.etree.ElementTree as ET
import json
import re


with open("dic_export.jpg", "r") as fd:
    dictionar = json.load(fd)
#print("Dictionar :  ", dictionar)


# split in sentences
with open('extract.txt','r') as f:
    content = f.read()
    # print(content)
    sentences = re.split(r'[.?]', str(content))
    #sentences = content.split(".")
# print("Sentences :  ", sentences)


xml_doc = ET.Element('TimeML')

# DOCNO tag
DOCNO = ET.SubElement(xml_doc,'DOCNO', type = 'date', temporalFunction = 'false').text = '19980108'

# DOCTYPE tag
DOCTYPE = ET.SubElement(xml_doc,'DOCTYPE',SOURCE='extract.txt').text = 'Vremuri de mult apuse'

# BODY tag
BODY = ET.SubElement(xml_doc,'BODY')

# TEXT tag
TEXT = ET.SubElement(BODY,'TEXT')
ok = 1
# s tag (sentences)
for i in sentences:
    s = ET.SubElement(TEXT, 's')
    for key, values in dictionar.items():
        for value in values:
            if value in i:
                # print("Value :  ", value)
                # TIMEEX tag
                tag = ET.SubElement(s, 'TIMEEX',id = 't' + str(ok), value = value, type = key, temporalFunction = 'true',functionInDocument = 'NONE').text = value
                ok = ok + 1
                # print(ok)





tree = ET.ElementTree(xml_doc)
tree.write('test.xml', encoding = 'UTF-8', xml_declaration = True)
