# -*- coding: utf-8 -*-

import codecs
import subprocess
import re
import os
import time, datetime

global NAME
global RUSSIAN
global LANG

names = [
    ['beautiful', 'eng', 'none'],
    ['handsome', 'eng', 'none'],
    ['lovely', 'eng', 'none'],
    ['krasivy', 'rus', u'красивый'],
    ['prekrasny', 'rus', u'прекрасный'],
    ['privlekatelny', 'rus', u'привлекательный'],
    [u'schön', 'ger', 'none'],
    [u'hübsch', 'ger', 'none'],
    [u'lieblich', 'ger', 'none']
]


#1. Обработка файла биграмм от Google
def make_bigrams():
    b = []
    f = codecs.open('googlebooks-' + LANG + '-all-2gram-20120701-' + NAME[0:2], 'r', 'utf-8')
    for line in f:
        line = line.replace('\t', ' ')
        line = line.lower()
        if LANG == 'rus':
            if RUSSIAN in line:
                r = line.split(' ')
                r[0] = re.sub(u'_.*', '', r[0])
                r[1] = re.sub(u'_.*', '', r[1])
                a = r[0] + ' ' + r[1]
                if a not in b:
                    b.append(a)
        else:
            if NAME in line:
                r = line.split(' ')
                r[0] = re.sub(u'_.*', '', r[0])
                r[1] = re.sub(u'_.*', '', r[1])
                a = r[0] + ' ' + r[1]
                if a not in b:
                    b.append(a)
    f.close()
    write_bigrams(b)
    

def write_bigrams(x):
    if not os.path.exists('final/1_all_bgrams/'):
        os.makedirs('final/1_all_bgrams/')
    d = codecs.open('final/1_all_bgrams/' + LANG +'_' + NAME + '.txt', 'w', 'utf-8')
    for element in x:
        d.write(element + '\r\n')
    d.close()


#2. Использование морфологических анализаторов
#RUS
def mystem():
    if not os.path.exists('final/2_morph/'):
        os.makedirs('final/2_morph/')
    p = subprocess.Popen([r'D:/kurs/mystem2.exe', r'-ci', r'-e', r'utf-8', r'D:/kurs/final/1_all_bgrams/' + LANG +'_' + NAME + '.txt', r'D:/kurs/final/2_morph/' + LANG +'_' + NAME + '.txt'])

    
#ENG
def treetagger_eng():
    if not os.path.exists('final/2_morph/'):
        os.makedirs('final/2_morph/')
    tr_begin()
    p1 = subprocess.Popen('D:', shell = True, stdout = subprocess.PIPE)
    p2 = subprocess.Popen('cd kurs/TreeTagger', shell = True, stdin = p1.stdout, stdout = subprocess.PIPE)
    p3 = subprocess.Popen([r'tree-tagger', r'-token', r'-lemma', r'lib/english-utf8.par', r'D:/kurs/final/1_all_bgrams/' + LANG +'_' + NAME + '.txt', r'D:/kurs/final/2_morph/' + LANG +'_' + NAME + '.txt'], shell = True, stdin = p2.stdout, stdout = subprocess.PIPE)
    tr_end()


#GER
def treetagger_ger():
    tr_begin()
    p1 = subprocess.Popen('D:', shell = True, stdout = subprocess.PIPE)
    p2 = subprocess.Popen('cd kurs/TreeTagger', shell = True, stdin = p1.stdout, stdout = subprocess.PIPE)
    p3 = subprocess.Popen([r'tree-tagger', r'-token', r'-lemma', r'lib/german-utf8.par', r'D:/kurs/final/1_all_bgrams/' + LANG +'_' + NAME + '.txt', r'D:/kurs/final/2_morph/' + LANG +'_' + NAME + '.txt'], shell = True, stdin = p2.stdout, stdout = subprocess.PIPE)
    tr_end()


def tr_begin():
    f = codecs.open('final/1_all_bgrams/' + LANG +'_' + NAME + '.txt', 'r', 'utf-8')
    t = f.read()
    f.close()
    
    t = t.replace(' ', '\r\n')
    
    d = codecs.open('final/1_all_bgrams/' + LANG +'_' + NAME + '.txt', 'w', 'utf-8')
    d.write('NAME\r\n' + t)
    d.close()

    
def tr_end():
    t = ''
    f = codecs.open(u'final/2_morph/' + LANG +'_' + NAME + u'.txt', 'r', 'utf-8')
    i = 1
    for line in f:
        if i % 2 != 0:
            line = line.rstrip()
        t = t + ' ' + line
        i += 1
    f.close()

    d = codecs.open(u'final/2_morph/' + LANG +'_' + NAME + u'.txt', 'w', 'utf-8')
    d.write(t)
    d.close()


#3. Проверка биграмм на A+S
#RUS
def rus_a_s():
    f = codecs.open('final/2_morph/' + LANG +'_' + NAME + '.txt', 'r', 'utf-8')
    bs = []
    
    for line in f:
        line = line.rstrip()
        
        if re.search(u'=S,', line) and re.search(u'=A=', line):
            line = line.split(' ')
            
            a = what(line[0])

            if a == 1:
                c = find_matches(line[0], line[1])
            elif a == 2:
                c = find_matches(line[1], line[0])
            elif a == 3:
                b = what(line[1])
                if b == 1:
                    c = find_matches(line[1], line[0])
                elif b == 2:
                    c = find_matches(line[0], line[1])
                elif b == 3:
                    c = find_matches(line[0], line[1])
                    c = find_matches(line[1], line[0])
            if c == 1:
                line[0] = re.sub(u'^.*?{', '', line[0])
                line[0] = re.sub(u'\??=.*$', '', line[0])
                line[1] = re.sub(u'^.*?{', '', line[1])
                line[1] = re.sub(u'\??=.*$', '', line[1])
                if RUSSIAN in line:
                    bigram = line[0] + ' ' + line[1]
                    if bigram not in bs:
                        bs.append(bigram)
                wr_ready_bs(bs)

    f.close()


def what(x):
    c = 0
    if '=S,' in x and '=A=' in x:
        return 3
    elif '=S,' in x:
        return 2
    elif '=A=' in x:
        return 1
    else:
        return 4


def for_S(x):
    x = re.sub(u'.*?{', '', x)
    x = x.replace('}', '')
    x = x.split(u'|')
    S = []
    for element in x:
        if 'S' in element:
            element = re.sub(u'^.*?S,', 'S,', element)
            S.append(element)
    return S


def for_A(x):
    x = re.sub(u'.*?{', '', x)
    x = x.replace('}', '')
    x = x.split(u'|')
    A = []
    for element in x:
        if 'A' in element:
            element = re.sub(u'^.*?A=', 'A=', element)
            A.append(element)
    return A


def find_matches(x, y):
    S = for_S(y)
    A = for_A(x)

    GENDER = [u'муж', u'жен', u'сред']
    CASE = [u'им', u'род', u'дат', u'вин', u'твор', u'пр']
    
    for variantS in S:
        for variantA in A:
            M = 0
            if u'ед' in variantS and u'ед' in variantA:
                M += 1
                for g in GENDER:
                    if g in variantS and g in variantA:
                        M += 1
            elif u'мн' in variantS and u'мн' in variantA:
                M = M + 2
            for c in CASE:
                if c in variantS and c in variantA:
                    M += 1
            if M == 3:
                return 1
    return 0


#ENG
def eng_a_s():
    t = []
    f = codecs.open('final/2_morph/' + LANG +'_' + NAME + '.txt', 'r', 'utf-8')
    for line in f:
        line = line.rstrip()
        line = line.split(' ')
        jj = line[1]
        nn = line[2]
        jj = jj.split('\t')
        nn = nn.split('\t')
        if (jj[1] == 'JJ') and (nn[1] == 'NN') and (jj[2] == NAME) and (nn[2] != '<unknown>'):
            bigram = jj[2] + ' ' + nn[2]
            if bigram not in t:
                t.append(bigram)
    f.close()
    wr_ready_bs(t)

#GER
def ger_a_s():
    t = ''
    f = codecs.open('final/2_morph/' + LANG +'_' + NAME + '.txt', 'r', 'utf-8')
    for line in f:
        line = line.rstrip()
        line = line.split(' ')
        jj = line[1]
        nn = line[2]
        jj = jj.split('\t')
        nn = nn.split('\t')
        if ('ADJ' in jj[1]) and (nn[1] == 'NN') and (jj[2] == NAME) and (nn[2] != '<unknown>'):
            bigram = jj[2] + ' ' + nn[2]
            if bigram not in t:
                t.append(bigram)
    f.close()
    wr_ready_bs(t)


def wr_ready_bs(x):
    if not os.path.exists('final/3_ready/'):
        os.makedirs('final/3_ready/')
    d = codecs.open('final/3_ready/' + LANG +'_' + NAME + '.txt', 'w', 'utf-8')
    for element in x:
        d.write(element + '\r\n')
    d.close()


#4. Перевод биграмм
def dict_for_translate(x):
    dicti = {}
    f = codecs.open('d_' + LANG + '_' + x + '.txt', 'r', 'utf-8')
    for line in f:
        line = line.rstrip()
        one, two = line.split(';')
        two = two.split(', ')
        dicti[one] = two
    f.close()
    return dicti


def translate(sublang1, sublang2):
    d1 = dict_for_translate(sublang1)
    d2 = dict_for_translate(sublang2)
    w = {}
    no_translate = []
    f = codecs.open('final/3_ready/' + LANG +'_' + NAME + '.txt', 'r', 'utf-8')
    for line in f:
        line = line.rstrip()
        line = line.lower()
        adj, noun = line.split(' ')
        tr1 = find_translation(d1, noun)
        tr2 = find_translation(d2, noun)
        tr = [tr1, tr2]
        if len(tr1) == 0 and len(tr2) == 0:
            no_translate.append(line)
        else:
            w[line] = tr
    write_translation(w)
    not_translated(no_translate)
    f.close()


def find_translation(d, noun):
    tr = []
    if noun in d:
        if len(d[noun]) > 0:
            for element in d[noun]:
                tr.append(element)
    return tr


def not_translated(x):
    if not os.path.exists('final/not_translated/'):
        os.makedirs('final/not_translated/')
    d = codecs.open('final/not_translated/' + LANG + '_' + NAME + '.txt', 'w', 'utf-8')
    for element in x:
        d.write(element + '\r\n')
    d.close()


def write_translation(x):
    if not os.path.exists('final/4_translated/' + LANG):
        os.makedirs('final/4_translated/' + LANG)
    d = codecs.open('final/4_translated/' + LANG + '/' + NAME + '.txt', 'w', 'utf-8')
    for bigramm in x:
        d.write(bigramm)
        for language in x[bigramm]:
            d.write('\t')
            if len(language) != 0:
                i = 1
                for word in language:
                    if i < len(language):
                        d.write(word + ';')
                    else:
                        d.write(word)
                    i += 1
    d.close()


#5. Создание единой таблицы
def result_lang(l):
    files = os.listdir('final/3_ready/')
    fin = {}
    lists = []
    adjs = []
    for filename in files:
        if filename[0:3] == l:
            nouns = []
            f = codecs.open('final/3_ready/' + filename, 'r', 'utf-8')
            for line in f:
                line = line.rstrip()
                adj, noun = line.split(' ')
                if adj not in adjs:
                    adjs.append(adj)
                fin[noun] = ''
                nouns.append(noun)
            f.close()
            lists.append(nouns)
    
    for noun in fin:
        i = 0
        for nouns_list in lists:
            if noun in nouns_list:
                a = fin[noun]
                a = a + adjs[i]
                fin[noun] = a
            a = fin[noun]
            a = a + ';'
            fin[noun] = a
            i += 1
            
    write_lang_result(fin, l)


def write_lang_result(x, l):
    if not os.path.exists('final/5_results/'):
        os.makedirs('final/5_results/')
    d = codecs.open('final/5_results/' + l + '.csv', 'w', 'cp1251')
    for element in x:
        d.write(element + ';' + x[element] + '\r\n')
    d.close()


def result():
    files_rus = os.listdir('final/4_translated/rus/')
    files_eng = os.listdir('final/4_translated/eng/')
    files_ger = os.listdir('final/4_translated/ger/')

    for filename_rus in files_rus:
        f_rus = codecs.open('final/4_translated/rus/' + filename_rus, 'r', 'utf-8')
        for filename_eng in files_eng:
            f_eng = codecs.open('final/4_translated/eng/' + filename_eng, 'r', 'utf-8')
            for rus_line in f_rus:
                rus_line = rus_line.rstrip()
                rus_rus, eng_rus, ger_rus = rus_line.split('\t')
                for eng_line in f_eng:
                    eng_line = eng_line.rstrip()
                    eng_eng, rus_eng, ger_eng = eng_line.split('\t')
##                    for word in rus_eng:
##                        if word
            f_eng.close()
        f_rus.close()
    

"""
ЗАПУСК ПРОГРАММЫ
"""
for element in names:
    print datetime.datetime.now()
    NAME = element[0]
    print NAME
    LANG = element[1]
    RUSSIAN = element[2]

    #make_bigrams()
##    if LANG == 'rus':
##        mystem()
##        rus_a_s()
##        translate('eng', 'ger')
##    elif LANG == 'eng':
####        treetagger_eng()
##        eng_a_s()
####        translate('rus', 'ger')
##    elif LANG == 'ger':
####        treetagger_ger()
##        ger_a_s()
####        translate('rus', 'eng')

result_lang('rus')
result_lang('eng')
result_lang('ger')
