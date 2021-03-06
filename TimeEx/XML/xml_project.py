import xml.etree.ElementTree as ET
import json
import re

#Se vor parsa datele din dictionar dupa care se va citii textul dintr-un fisier txt ce va fii impartit in propozitii si se vor adauga tagurile corespunzatoare pentru fiecare sectiune. Folosind datele din dictionare identificam diversele elemente temporale din text pe care le incadram in tagul TIMEEX cu valorile corespunzatoare (id, value, type etc).



input_file = ""


def setare_input(input_file_tmp):
    global input_file
    input_file = input_file_tmp


def rulare():
    with open("tmp\\dict_export", "r") as fd:
        dictionar = json.load(fd)
    print("Dictionar :  ", dictionar)

    # split in sentences
    with open(input_file, 'r') as f:
        content = f.read()
        # print(content)
    sentences = content.split("?.!,")
    print(sentences)
    print()
    # sentences = content.split(".")
    # print("Sentences :  ", sentences)

    xml_doc = ET.Element('TimeML')

    # DOCNO tag
    DOCNO = ET.SubElement(xml_doc, 'DOCNO', type='date', temporalFunction='false').text = '19980108'

    # DOCTYPE tag
    DOCTYPE = ET.SubElement(xml_doc, 'DOCTYPE', SOURCE='extract.txt').text = 'TimeEx'

    # BODY tag
    BODY = ET.SubElement(xml_doc, 'BODY')

    # TEXT tag
    TEXT = ET.SubElement(BODY, 'TEXT')
    ok = 1
    # s tag (sentences)
    for i in sentences:
        s = ET.SubElement(TEXT, 's')
        for key, values in dictionar.items():
            for value in values:
                if value in i:
                    # print("Value :  ", value)
                    # TIMEEX tag
                    tag = ET.SubElement(s, 'TIMEEX', id='t' + str(ok), value=value, type=key, temporalFunction='true',
                                        functionInDocument='NONE').text = value
                    ok = ok + 1
                    # print(ok)

    tree = ET.ElementTree(xml_doc)
    tree.write('output/exemplu.xml', encoding='UTF-8', xml_declaration=True)


if __name__ == '__main__':
    # raise Exception("Run the app from main.py")
    setare_input("..\\..\\input\\extract.txt")
    rulare()
