# -*- coding: utf-8 -*-

import codecs
import subprocess
import re
import os
import time, datetime

global NAME
global RUSSIAN
global LANG

NAMES = [
    ['soft', 'eng', 'none'],
    ['mild', 'eng', 'none'],
    ['sanft', 'ger', 'none'],
    ['weich', 'ger', 'none'],
    ['magkiy', 'rus', u'мягкий']
]


#1. Обработка файла биграмм от Google
def make_bigrams():
    b = []
    f = codecs.open('googlebooks-' + LANG + '-all-2gram-20120701-' + NAME[0:2], 'r', 'utf-8')
    for line in f:
        line = line.replace('\t', ' ')
        line = line.lower()
        if LANG == 'rus':
            if RUSSIAN[0:-3] in line:
                r = line.split(' ')
                if '_' in r[0] and '_' in r[1]:
                    r1 = r[0].split(u'_')
                    r2 = r[1].split(u'_')
                    if r1[1] == 'adj' and r2[1] == 'noun' and r2[0] != '':
                        a = r1[0] + ' ' + r2[0]
                        if a not in b:
                            b.append(a)
        else:
            if NAME in line:
                r = line.split(' ')
                if '_' in r[0] and '_' in r[1]:
                    r1 = r[0].split(u'_')
                    r2 = r[1].split(u'_')
                    if r1[1] == 'adj' and r2[1] == 'noun' and r2[0] != '':
                        a = r1[0] + ' ' + r2[0]
                        if a not in b:
                            b.append(a)
    f.close()
    write_bigrams(b)


def write_bigrams(x):
    if not os.path.exists('final/1_adj_noun/'):
        os.makedirs('final/1_adj_noun/')
    d = codecs.open('final/1_adj_noun/' + LANG +'_' + NAME + '.txt', 'w', 'utf-8')
    for element in x:
        d.write(element + '\r\n')
    d.close()


#2. Использование морфологических анализаторов
#RUS
def mystem():
    if not os.path.exists('final/2_morph'):
        os.makedirs('final/2_morph/')
    p = subprocess.Popen([r'D:/kurs/mystem2.exe',
                          r'-ci',
                          r'-e',
                          r'utf-8',
                          r'D:/kurs/final/1_adj_noun/' + LANG +'_' + NAME + '.txt',
                          r'D:/kurs/final/2_morph/' + LANG +'_' + NAME + '.txt'])


#ENG
def treetagger_eng():
    tr_begin()
    p = subprocess.Popen([r'D:/kurs/TreeTagger/bin/tree-tagger.exe',
                          r'-token',
                          r'-lemma',
                          r'D:/kurs/TreeTagger/lib/english-utf8.par',
                          r'D:/kurs/final/2_morph/prett/' + LANG + '_' + NAME + '.txt',
                          r'D:/kurs/final/2_morph/' + LANG + '_' + NAME + '.txt'])
    tr_end()


#GER
def treetagger_ger():
    tr_begin()
    p = subprocess.Popen([r'D:/kurs/TreeTagger/bin/tree-tagger.exe',
                          r'-token',
                          r'-lemma',
                          r'D:/kurs/TreeTagger/lib/german-utf8.par',
                          r'D:/kurs/final/2_morph/prett/' + LANG + '_' + NAME + '.txt',
                          r'D:/kurs/final/2_morph/' + LANG + '_' + NAME + '.txt'])
    tr_end()


def tr_begin():
    f = codecs.open('final/1_adj_noun/' + LANG +'_' + NAME + '.txt', 'r', 'utf-8')
    t = ''
    for line in f:
        if ' ' in line and NAME in line:
            line = line.split(' ')
            if line[1] != '':
                t = t + line[0] + '\r\n' + line[1]
    f.close()

    if not os.path.exists('final/2_morph/prett/'):
        os.makedirs('final/2_morph/prett/')
    d = codecs.open('final/2_morph/prett/' + LANG + '_' + NAME + '.txt', 'w', 'utf-8')
    d.write(t)
    d.close()

    
def tr_end():
    t = ''
    while not os.path.exists(u'final/2_morph/' + LANG + '_' + NAME + u'.txt'):
        t = ''
    time.sleep(3)
    f = codecs.open(u'final/2_morph/' + LANG + '_' + NAME + u'.txt', 'r', 'utf-8')
    i = 1
    for line in f:
        if i % 2 != 0:
            line = line.rstrip()
        t = t + ';' + line
        i += 1
    f.close()

    d = codecs.open(u'final/2_morph/' + LANG + '_' + NAME + u'.txt', 'w', 'utf-8')
    d.write(t)
    d.close()
    

#3. Проверка биграмм на A+S
#RUS
def rus_a_s():
    while not os.path.exists('final/2_morph/' + LANG +'_' + NAME + '.txt'):
        time.sleep(3)
    f = codecs.open('final/2_morph/' + LANG +'_' + NAME + '.txt', 'r', 'utf-8')
    bs = []
    for line in f:
        line = line.rstrip()

        if ' ' in line:
            line = line.split(' ')

            if '=A=' in line[0] and '=S,' in line[1]:
                c = find_matches(line[0], line[1])
           
                if c == 1:
                    line[0] = re.sub(u'^.*?{', '', line[0])
                    line[0] = re.sub(u'\??=.*$', '', line[0])
                    line[1] = re.sub(u'^.*?{', '', line[1])
                    line[1] = re.sub(u'\??=.*$', '', line[1])
                    if RUSSIAN in line:
                        bigram = line[0] + ' ' + line[1]
                        if bigram not in bs:
                            bs.append(bigram)
    f.close()
    wr_ready_bs(bs)
    

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
        
    f = codecs.open('final/2_morph/' + LANG + '_' + NAME + '.txt', 'r', 'utf-8')
    for line in f:
        line = line.rstrip()
        line = re.sub('^;', '', line)
        adj, noun = line.split(';')
        adj = adj.split('\t')
        noun = noun.split('\t')
        
        if 'JJ' in adj[1] and noun[1] == 'NN':
            if adj[0] == NAME or adj[0] == NAME + 'er' or adj[0] == NAME + 'est':
                bigram = adj[2] + ' ' + noun[0]
                t.append(bigram)
                
    f.close()
    wr_ready_bs(t)


#GER
def ger_a_s():
    t = []
        
    f = codecs.open('final/2_morph/' + LANG + '_' + NAME + '.txt', 'r', 'utf-8')
    for line in f:
        line = line.rstrip()
        line = re.sub('^;', '', line)
        adj, noun = line.split(';')
        adj = adj.split('\t')
        noun = noun.split('\t')

        if 'ADJ' in adj[1] and noun[1] == 'NN':
            if re.match(NAME + u'(est|er)?e[rnms]?$', adj[0]):
                bigram = adj[2] + ' ' + noun[0]
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
def translate():
    
    result_line = {}
    i = 1
    for element in os.listdir('final/3_ready'):
        if NAME not in element:
            i += 1
            main_foreign_word = element[4:-4]
            main_foreign_lang = element[0:3]

            foreign_nouns = make_list_foreign_nouns(element)  
            result_line = main_file_searching_translations(main_foreign_lang, main_foreign_word, foreign_nouns, result_line, i)

    result_line = make_mas(result_line)
    result_line = make_categories(result_line, os.listdir('final/3_ready'), 0)
    write_translation(result_line)


def make_list_foreign_nouns(filename):
    nouns = []
    f = codecs.open('final/3_ready/' + filename, 'r', 'utf-8')
    for line in f:
        line = line.rstrip()
        adj, noun = line.split(' ')
        nouns.append(noun)
    f.close()
    return nouns


def main_file_searching_translations(language, word, foreign, results_file, i):
    f = codecs.open('final/3_ready/' + LANG + '_' + NAME + '.txt', 'r', 'utf-8')
    if language != LANG:
        d = dict_for_translate(language)
    for line in f:
        line = line.rstrip()
        line = line.lower()
        adj, noun = line.split(' ')
        words = []
        if noun not in results_file:
            results_file[noun] = words
            results_file[noun].append(adj)
                    
        if len(results_file[noun]) != i:
            if language != LANG:
                tr = find_translation(d, noun)

                if tr == []:
                    results_file[noun].append(0)
                        
                else:               
                    for n in tr:
                        if n in foreign:
                            results_file[noun].append(word)
                            break
                    if len(results_file[noun]) == i - 1:
                        results_file[noun].append('')
                
            else:
                for n in foreign:
                    if n == noun:
                        results_file[noun].append(word)
                        break
                if len(results_file[noun]) == i - 1:
                    results_file[noun].append('')
        
    f.close()
    return results_file


def dict_for_translate(x):
    dicti = {}
    f = codecs.open('d_' + LANG + '_' + x + '.txt', 'r', 'utf-8')
    for line in f:
        line = line.rstrip()
        one, two = line.split(';')
        two = two.split(',')
        dicti[one] = two
    f.close()
    return dicti


def find_translation(d, noun):
    if noun in d:
        if len(d[noun]) > 0:
            return d[noun]
    else:
        return []


def make_categories(x, filenames, i):
    if i >= len(filenames):
        return x
    mas1 = []
    mas2 = []
    n = filenames[i]
    for element in x:
        if n[4:-4] in element:
            mas1.append(element)
        else:
            mas2.append(element)
    mas1 = make_categories(mas1, filenames, i + 1)
    mas2 = make_categories(mas2, filenames, i + 1)
    mas = mas1 + mas2
    return mas


def write_translation(x):
    if not os.path.exists('final/4_translated/'):
        os.makedirs('final/4_translated/')
    d = codecs.open('final/4_translated/' + LANG + '_' + NAME + '.csv', 'w', 'cp1251')
    for a in x:
        if LANG == 'ger':
            a = a.replace(u'ö', 'o:')
            a = a.replace(u'ü', 'u:')
            a = a.replace(u'ä', 'a:')
            a = a.replace(u'Ö', 'O:')
            a = a.replace(u'Ü', 'U:')
            a = a.replace(u'Ä', 'A:')
            a = a.replace(u'ß', 'SS')
        d.write(a[:-1] + '\n')
    d.close()
        
        
#ДОП запись невошедших элементов
def not_translated(x):        
    if not os.path.exists('final/not_translated/'):
        os.makedirs('final/not_translated/')
        
    d = codecs.open('final/not_translated/' + LANG + '_' + NAME + '.txt', 'w', 'utf-8')
    for element in x:
        d.write(element + '\r\n')
    d.close()


def make_mas(x):
    y = []
    z = []
    i = 0
    for filename in os.listdir('final/4_translated'):
        if filename[0:3] == LANG:
            i += 1
    for element in x:
        a = ''
        j = 0
        for word in x[element]:
            if word == 0:
                j += 1
                a = a + ';'
            else:
                a = a + word + ';'
        if j == len(x[element]) - i:
            z.append(element)
        else:
            y.append(element + ';' + a)
    not_translated(z)
    return y



"""
ЗАПУСК ПРОГРАММЫ
"""

#1. Обработка биграмм
for element in NAMES:
    print datetime.datetime.now()
    NAME = element[0]
    print NAME
    LANG = element[1]
    RUSSIAN = element[2]

    make_bigrams()
    if LANG == 'rus':
        mystem()
        rus_a_s()
    if LANG == 'eng':
        treetagger_eng()
        eng_a_s()
    if LANG == 'ger':
        treetagger_ger()
        ger_a_s()
      
    print datetime.datetime.now()

#2. Поиск переводных эквивалентов
for element in NAMES:
    print datetime.datetime.now()
    NAME = element[0]
    print NAME
    LANG = element[1]
    RUSSIAN = element[2]

    translate()
      
    print datetime.datetime.now()    
