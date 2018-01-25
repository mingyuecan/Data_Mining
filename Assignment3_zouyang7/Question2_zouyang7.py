## Assignment 3 Question 2
## Name: Zixin Ouyang

import pandas as pd
import numpy as np
import itertools
from collections import defaultdict, OrderedDict

text_file = open("/Users/Constance/Desktop/Data.txt", "r")
linelist=[l.strip('\n') for l in text_file.readlines()]

newlist=[]
for i in range(0,len(linelist)):
    new=linelist[i].split(',')
    new1=[float(j) for j in new]
    newlist.append(new1)

seqs=[]
for i in newlist[1:]:
    print
    new2=[int(j) for j in i]
    seqs.append(new2)
    
sup=newlist[0][0]
res=newlist[0][1]

def _sort_transactions_by_freq(
        transactions, key_func, reverse_int=False,
        reverse_ext=False, sort_ext=True):
    key_seqs = [{key_func(i) for i in sequence} for sequence in transactions]
    frequencies = get_frequencies(key_seqs)

    asorted_seqs = []
    for key_seq in key_seqs:
        if not key_seq:
            continue
        l = [(frequencies[i], i) for i in key_seq]
        l.sort(reverse=reverse_int)
        asorted_seqs.append(tuple(l))
    if sort_ext:
        asorted_seqs.sort(reverse=reverse_ext)

    return (asorted_seqs, frequencies)


def get_frequencies(transactions):
    frequencies = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            frequencies[item] += 1
    return frequencies

def _new_relim_input(size, key_map):
    i = 0
    l = []
    for key in key_map:
        if i >= size:
            break
        l.append(((0, key), []))
        i = i + 1
    return l


def _get_key_map(frequencies):
    l = [(frequencies[k], k) for k in frequencies]
    l.sort(reverse=True)
    key_map = OrderedDict()
    for i, v in enumerate(l):
        key_map[v] = i
    return key_map


def get_relim_input(transactions, key_func=None):
    if key_func is None:
        def key_func(e):
            return e

    (asorted_seqs, frequencies) = _sort_transactions_by_freq(
        transactions, key_func)
    key_map = _get_key_map(frequencies)

    relim_input = _new_relim_input(len(key_map), key_map)
    for seq in asorted_seqs:
        if not seq:
            continue
        index = key_map[seq[0]]
        ((count, char), lists) = relim_input[index]
        rest = seq[1:]
        found = False
        for i, (rest_count, rest_seq) in enumerate(lists):
            if rest_seq == rest:
                lists[i] = (rest_count + 1, rest_seq)
                found = True
                break
        if not found:
            lists.append((1, rest))
        relim_input[index] = ((count + 1, char), lists)
    return (relim_input, key_map)


def relim(rinput, min_support=2):
    fis = set()
    report = {}
    _relim(rinput, fis, report, min_support)
    return report


def _relim(rinput, fis, report, min_support):
    (relim_input, key_map) = rinput
    n = 0
    a = relim_input
    while len(a) > 0:
        item = a[-1][0][1]
        s = a[-1][0][0]
        if s >= min_support:
            fis.add(item[1])
            report[frozenset(fis)] = s
            b = _new_relim_input(len(a) - 1, key_map)
            rest_lists = a[-1][1]

            for (count, rest) in rest_lists:
                if not rest:
                    continue
                k = rest[0]
                index = key_map[k]
                new_rest = rest[1:]
                # Only add this rest if it's not empty!
                ((k_count, k), lists) = b[index]
                if len(new_rest) > 0:
                    lists.append((count, new_rest))
                b[index] = ((k_count + count, k), lists)
            n = n + 1 + _relim((b, key_map), fis, report, min_support)
            fis.remove(item[1])

        rest_lists = a[-1][1]
        for (count, rest) in rest_lists:
            if not rest:
                continue
            k = rest[0]
            index = key_map[k]
            new_rest = rest[1:]
            ((k_count, k), lists) = a[index]
            if len(new_rest) > 0:
                lists.append((count, new_rest))
            a[index] = ((k_count + count, k), lists)
        a.pop()
    return n

relim_input = get_relim_input(seqs)
report = relim(relim_input, min_support=len(seqs)*sup)

newrep=[]
for i in report:
    newrep.append(list(i))
    
def sub_lists(my_list):
    subs = [[]]
    for i in range(len(my_list)):
        n = i+1
        while n <= len(my_list):
            sub = my_list[i:n]
            subs.append(sub)
            n += 1
    newsubs=[list(j) for j in set(map(tuple, subs))]
    return newsubs

def get_all(k):
    al=[]
    result=[]
    for j in k[1]:
        if len(j)>=len(k[0]):
            if set(k[0]).issubset(set(j))==True:
                if len(k[0])==1:
                    result=k[0]
                elif len(k[0])>1:
                    al.append(j)
    for i in al:
        if len(i)==min(map(len, al)):
            result=i
    if result==[]:
        nr='NA'
    elif result!=[]:
        nr=len(set(result)-set(k[0]))
    return nr

def my_test(x,y):
    return y/len(x)

def count_true(x):
    count=0
    for i in x:
        if i==True:
            count=count+1
    return count

alllist=[i for i in map(sub_lists, seqs)]
fl=list(itertools.product(newrep, alllist))

newf=pd.DataFrame(fl, columns=['itemset', 'sequence'])
newf['noutliers']=newf.apply(get_all, axis=1)
newf['noutliers'].replace('NA', np.nan,inplace=True)
newf.dropna(inplace=True)
newf['percent']=newf.apply(lambda row: my_test(row['itemset'], row['noutliers']), axis=1)
newf['satisfy']=newf.percent.between(0,res)
newf['itemsets']=newf['itemset'].apply(tuple)
result=newf.groupby('itemsets')['satisfy'].apply(list)
newresult=pd.DataFrame(result).reset_index()
newresult['tcount']=newresult.satisfy.apply(count_true)
newresult.itemsets=newresult.itemsets.apply(list)
final=newresult['itemsets'][newresult['tcount']>=len(seqs)*sup]

with open('Desktop/final.txt', 'w') as f:
    for i in final:
        print(",".join(str(x) for x in i), file=f)
