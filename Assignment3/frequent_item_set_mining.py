## Assignment 3 
## Name: Zixin Ouyang

import pandas as pd
import numpy as np
import itertools


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

from pymining import itemmining

relim_input = itemmining.get_relim_input(seqs)
report = itemmining.relim(relim_input, min_support=len(seqs)*sup)

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
