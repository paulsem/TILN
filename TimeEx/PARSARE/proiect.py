import json
import re
import os
from sutime import SUTime
from TimeEx.XML import xml_project
from googletrans import Translator

input_file = ""
dictionar = {}
path = ""


# Folosim expresii regulate si expresii compuse pentru a extrage expresiile temporale dintr-un text pe care il citim


def convertor(num):
    sub20 = ['zero', 'unu', 'doi', 'trei', 'patru', 'cinci', 'sase', 'sapte', 'opt', 'noua', 'zece', 'unsprezece',
             'doisprezece', 'treisprezece', 'paisprezece', 'cincisprezece', 'saisprezece', 'saptesprezece',
             'optsprezece', 'nouasprezece']
    zeci = ['douazeci si', 'treizeci si', 'patruzeci si', 'cincizeci si', 'saizeci si', 'saptezeci si',
            'optzeci si', 'nouazeci si']
    zecismp = ['douazeci', 'treizeci', 'patruzeci', 'cincizeci', 'saizeci', 'saptezeci', 'optzeci', 'nouazeci']
    peste100 = {100: 'o suta', 1000: 'o mie'}
    peste200 = {100: 'sute', 1000: 'mii'}
    sub220 = ['zero', 'unu', 'doua', 'trei', 'patru', 'cinci', 'sase', 'sapte', 'opt', 'noua']

    if 9 < num < 100 and int(str(num)[1:]) == 0 and int(str(num)[:1]) != 1:
        return zecismp[int(str(num)[:1]) - 2]
    if num < 20:
        return sub20[num]
    if num < 100:
        return zeci[int(num / 10) - 2] + ('' if num % 10 == 0 else ' ' + sub20[num % 10])

    aproximatie = max([key for key in peste100.keys() if key <= num])
    if num >= 2000:
        return sub220[int(str(num)[:1])] + ' ' + peste200[aproximatie] + (
            '' if num % aproximatie == 0 else ' ' + convertor(num % aproximatie))

    if num >= 1000:
        return peste100[aproximatie] + (
            '' if num % aproximatie == 0 else ' ' + convertor(num % aproximatie))

    if num >= 200:
        return sub220[int(str(num)[:1])] + ' ' + peste200[aproximatie] + (
            '' if num % aproximatie == 0 else ' ' + convertor(num % aproximatie))

    if num >= 100:
        return peste100[aproximatie] + (
            '' if num % aproximatie == 0 else ' ' + convertor(num % aproximatie))


def lista_numere(text, timp, data):
    lista_cu_numere = []
    for i in range(10000):
        lista_cu_numere.append(convertor(i))

    timp_complex = []
    data_complex = []
    for index, numar in enumerate(lista_cu_numere):
        if numar in text:
            if index < 20:
                timp_complex.extend(parsare_cifre_text(text, timp, numar))
            else:
                timp_complex.extend(parsare_cifre_text(text, timp, numar))
                timp_complex.extend(parsare_cifre_text_complex(text, timp, numar))
            if index < 20:
                data_complex.extend(parsare_cifre_text(text, data, numar))
            else:
                data_complex.extend(parsare_cifre_text(text, data, numar))
                data_complex.extend(parsare_cifre_text_complex(text, data, numar))
    secund = ["una", "unul", "o", "doua"]
    for numar in secund:
        if numar in text:
            timp_complex.extend(parsare_cifre_text(text, timp, numar))
            data_complex.extend(parsare_cifre_text(text, data, numar))

    return timp_complex, data_complex


def importare_text(input_file):
    with open("input\\extract.txt", "r") as fd:
        return fd.read()


def retezare(lista):
    tmp = []
    for item in lista:
        if "\n" == item or "+\n" == item:
            pass
        else:
            for word in item.split(", "):
                tmp_word = word
                tmp_word = tmp_word.replace(",", "")
                tmp_word = tmp_word.replace("\n", "")
                tmp.append(tmp_word)
    return tmp


def importare_dictionar():
    tmp = []
    ok = -2
    timp_simplu, data_simplu, timp_compus, data_compus = 0, 0, 0, 0

    # TimeEx/PARSARE/
    with open(r"TimeEx/PARSARE/romana.txt", "r") as fd:
        line = fd.readline()
        while line:
            tmp.append(line)
            if line == "+\n" and ok == -2:
                lunile = tmp
                tmp = []
                ok = -1
            if line == "\n" and ok == 0:
                timp_simplu = tmp
                tmp = []
                ok = 1
            if line == "\n" and ok == -1:
                ok = 0
            if line == "+\n" and ok == 1:
                data_simplu = tmp
                tmp = []
                ok = 2
            if line == "\n" and ok == 3:
                timp_compus = tmp
                tmp = []
                ok = 4
            if line == "\n" and ok == 2:
                ok = 3
            line = fd.readline()
        data_compus = tmp

    lunile = retezare(lunile)
    timp_simplu = retezare(timp_simplu)
    data_simplu = retezare(data_simplu)
    timp_compus = retezare(timp_compus)
    data_compus = retezare(data_compus)

    return lunile, timp_simplu, data_simplu, timp_compus, data_compus


def parsare_cifre(text):
    timp_tmp = []
    data_tmp = []

    tmp_timp = re.findall("[0-9]{1,2}:[0-9]{1,2}", text)
    if tmp_timp:
        [timp_tmp.append(x) for x in tmp_timp]

    tmp_data = re.findall("[0-9]{0,2}\.[0-9]{0,2}\.[0-9]{4}", text)
    if tmp_data:
        [data_tmp.append(x) for x in tmp_data]

    tmp_data = re.findall("[0-9]{0,2}-[0-9]{0,2}-[0-9]{4}", text)
    if tmp_data:
        [data_tmp.append(x) for x in tmp_data]

    tmp_data = re.findall("[0-9]{0,2}/[0-9]{0,2}/[0-9]{4}", text)
    if tmp_data:
        [data_tmp.append(x) for x in tmp_data]

    tmp_data = re.findall("\s+[0-9]{4}\s+", text)
    if tmp_data:
        [data_tmp.append(x) for x in tmp_data]

    tmp_data = re.findall("\s+'[0-9]{2}\s+", text)
    if tmp_data:
        [data_tmp.append(x) for x in tmp_data]

    return timp_tmp, data_tmp


def parsare_text(text):
    text = text.lower()
    text = text.replace(",", "")
    text = text.replace("(", "")
    text = text.replace(")", "")
    text = text.replace(".", "")
    text = text.replace("?", "")
    text = text.replace(";", "")
    text = text.replace("\"", "")
    text = text.replace(":", "")
    text = text.replace("\'", "")
    return text


def parsare_simplu(text, timp, data):
    text = parsare_text(text)
    timp_simplu = []
    data_simplu = []
    for line in text.split(" "):
        for timp_tmp in timp:
            if line == timp_tmp:
                timp_simplu.append(line)
    for data_tmp in data:
        if data_tmp in text:
            data_simplu.append(data_tmp)
    return timp_simplu, data_simplu


def parsare_complex(text, timp, data):
    timp_complex = parsare_cifre_text(text, timp)
    timp_complex.extend(parsare_cifre_text_complex(text, timp))

    data_complex = parsare_cifre_text(text, data)
    data_complex.extend(parsare_cifre_text_complex(text, data))
    return timp_complex, data_complex


def parsare_cifre_text(text, cuvinte, cifre="[0-9]{1,2}"):
    cuvinte_gasite = []
    pattern = re.compile(r"(" + cifre + ")\s([A-Z]*[a-z]+)")
    for match in re.finditer(pattern, text):
        if match.group(2).lower() in cuvinte:
            cuvinte_gasite.append(match.group())
    pattern = re.compile(r"([A-Z]*[a-z]+)\s(" + cifre + ")\s")
    for match in re.finditer(pattern, text):
        if match.group(1).lower() in cuvinte:
            cuvinte_gasite.append(match.group())
    return cuvinte_gasite


def parsare_cifre_text_complex(text, cuvinte, cifre="[0-9]{1,2}"):
    cuvinte_gasite = []
    pattern = re.compile(r"(" + cifre + ")\s(de*)\s([A-Z]*[a-z]+)")
    for match in re.finditer(pattern, text):
        if match.group(3).lower() in cuvinte:
            cuvinte_gasite.append(match.group())
    pattern = re.compile(r"([A-Z]*[a-z]+)\s(de*)\s(" + cifre + ")")
    for match in re.finditer(pattern, text):
        if match.group(1).lower() in cuvinte:
            cuvinte_gasite.append(match.group())
    return cuvinte_gasite


def parsare_luni(text, luni):
    luni_timp = []
    pattern = re.compile(r"luna\s([a-z]{3,10})")
    for match in re.finditer(pattern, text.lower()):
        if match.group(1).lower() in luni:
            luni_timp.append(match.group())
    return luni_timp


def adaugare_dict(valoare, tag):
    global dictionar
    if valoare:
        try:
            [dictionar[tag].append(x) for x in valoare if x not in dictionar[tag]]
        except:
            dictionar[tag] = valoare.copy()


def merge_dict(dict_primit):
    global dictionar
    dictionar = dict_primit


def setare_input(input_file_tmp):
    global input_file
    input_file = input_file_tmp


def convert_to_romana(exp):
    translator = Translator()
    traducere = translator.translate(exp, src='en', dest="ro").text
    return traducere


def complex_words(text):
    lista = []
    with open(r"TimeEx/PARSARE/future.txt", "r") as fd:
        words = fd.readline()
        verbs = fd.readline()
    for x in words[:-1].split(", "):
        for y in verbs.split(", "):
            if y.replace("x", x) in text.lower():
                lista.append(y.replace("x", x))
    lista_tmp = lista.copy()
    for x in range(len(lista_tmp)):
        for y in lista_tmp[x + 1:]:
            if lista_tmp[x] in y:
                lista.remove(lista_tmp[x])

    for i in range(2):
        if i == 0:
            cifre = "([0-9]+)"
        if i == 1:
            cifre = "([MDCLXVI]+)"
        pattern = re.compile(r"([A-Z]*[a-z]+\s[a-z]+)\s" + cifre)
        for match in re.finditer(pattern, text):
            if match.group(1).lower() in lista:
                lista[lista.index(match.group(1).lower())] = match.group()
        pattern = re.compile(r"([A-Z]*[a-z]+\s[a-z]+\s[a-z]+)\s" + cifre)
        for match in re.finditer(pattern, text):
            if match.group(1).lower() in lista:
                lista[lista.index(match.group(1).lower())] = match.group()

    return lista


def sutime_function(text):
    translator = Translator()
    traducere = translator.translate(text, src='ro', dest="en").text

    java_target = "java\\target"
    jar_files = os.path.join(os.path.dirname(__file__), java_target)
    sutime = SUTime(jars=jar_files, mark_time_ranges=True)

    ttext = []
    ttype = []
    tmpdictionar = {}

    for x in sutime.parse(traducere):
        for value, key in x.items():
            if value == "text":
                valoare = convert_to_romana(key)
                ttext.append(valoare)
            elif value == "type":
                valoare2 = convert_to_romana(key)
                ttype.append(valoare2)

    for x in range(len(ttext)):
        try:
            tmpdictionar[ttype[x]].append(ttext[x])
        except:
            tmpdictionar[ttype[x]] = [ttext[x]]

    return tmpdictionar


def rulare(debug=False, sutimev=False, xml=True):
    global dictionar
    dictionar = {}
    text = importare_text(input_file)
    if sutimev:
        merge_dict(sutime_function(text))

        if debug:
            print()
            print("Dictionar:\t", dictionar)

    if not sutimev:
        dict_lunile, dict_timp_simplu, dict_data_simplu, dict_timp_complex, dict_data_complex = importare_dictionar()

        timp_cifre, data_cifre = parsare_cifre(text)  # 15:30,  02.04.1999
        timp_simplu, data_simplu = parsare_simplu(text, dict_timp_simplu, dict_data_simplu)  # acuma, marti ieri
        timp_complex, data_complex = parsare_complex(text, dict_timp_complex, dict_data_complex)  # 7 ore, 20 de luni
        lunile = parsare_luni(text, dict_lunile)  # luna mai luna iunie
        lunile2 = parsare_cifre_text(text, dict_lunile)  # 25 aprilie 10 iulie
        timp_text, data_text = lista_numere(text, dict_timp_complex, dict_data_complex)  # doua ore sapte luni
        lista_complex = complex_words(text)

        adaugare_dict(timp_complex, "DURATA")
        adaugare_dict(data_complex, "DATA")
        adaugare_dict(timp_text, "DURATA")
        adaugare_dict(data_text, "DURATA")
        adaugare_dict(lunile, "DATA")
        adaugare_dict(lunile2, "DATA")
        adaugare_dict(data_cifre, "DATA")
        adaugare_dict(data_simplu, "DATA")
        adaugare_dict(lista_complex, "DATA")
        adaugare_dict(timp_cifre, "ORA")
        adaugare_dict(timp_simplu, "ORA")

        if debug:
            print("timp_cifre:\t\t", timp_cifre)
            print("data_cifre:\t\t", data_cifre)
            print("timp_simplu:\t", timp_simplu)
            print("data_simplu:\t", data_simplu)
            print("timp_complex:\t", timp_complex)
            print("data_complex:\t", data_complex)
            print("Lunile:\t\t\t", lunile, lunile2)
            print("timp_text:\t", timp_text)
            print("data_text:\t", data_text)
            print()
            print("Dictionar:\t", dictionar)

    if sutimev:
        with open("tmp/dict_export_sutime", "w") as fd:
            json.dump(dictionar, fd)
    else:
        with open("tmp/dict_export", "w") as fd:
            json.dump(dictionar, fd)

    if xml:
        xml_project.setare_input(input_file)
        xml_project.rulare()

    return dictionar


def sutime_dict():
    with open("tmp/dict_export_sutime", "r") as fd:
        return json.load(fd)


def compare(sutimev=False):
    if sutimev:
        dictionar_sutime = rulare(debug=False, sutimev=sutimev, xml=False)
    else:
        dictionar_sutime = sutime_dict()
    print("\nComparing the 2 functions\n")
    print("Sutime - Keep in mind that the text has been translated from Romanian to English and back to Romanian")
    for x, y in dictionar_sutime.items():
        print(f"Gasit pt {x} {len(y)} |", y)

    dictionar_a_nostru = rulare(debug=False, sutimev=False, xml=False)
    print("\nOurs")
    for x, y in dictionar_a_nostru.items():
        print(f"Gasit pt {x} {len(y)} |", y)


if __name__ == '__main__':
    # raise Exception("Run the app from main.py")
    setare_input("input\\extract.txt")
    compare()
