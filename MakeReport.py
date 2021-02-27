import pandas as pd
import numpy as np
import plotly.graph_objects as go
from matplotlib import pyplot as plt
import random
import csv
import math
import time
import json
import functools

def init (file_path, out_file):
    data = pd.read_csv(file_path+'/results.csv')
    frame = pd.DataFrame()
    frame['user_ids'] = data['session_id'] #we add a column with user ids
    frame['scores'] = data['score'] #add a column with all the scores people got for each task

    nums = list(frame['scores']) #get a list of every single point received
    #print(nums,'screenshot #1')
    peop = len(list(set(list(data['session_id'])))) #how many people participated
    n = list(set(list(data['task_no']))) #all tasks numbers
    n.sort(reverse=True)
    n = n[0] #number of tasks

    init_list= []
    p = 25 #скольким процентам давать дипломы
    iter = 2 #сколько итераций
    # let's get the default fraction
    for i in data['max_score'][:n]:
        init_list.append(i)
    print(init_list)
    print('идеальное количество дипломов',int(peop*p/100))
    scaling = []
    for i in range(len(nums)):
        scaling.append(
            nums[i] / init_list[i % n])  # divide each score by the maximum possible score for THAT task
    #print(scaling, 'the fractions we will multiply the new scores by soon')
    #let's count the difficulties of tasks
    def get_fraction(src_dir):
        task_id_to_cnt = {}
        task_id_to_ok_cnt = {}
        with open(src_dir + '/results.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                if row['verdict'] == 'none':
                    continue
                task_id = int(row['task_id'])

                cnt = task_id_to_cnt.get(task_id, 0)
                task_id_to_cnt[task_id] = cnt + 1

                if row['verdict'] == 'ok':
                    cnt_ok = task_id_to_ok_cnt.get(task_id, 0)
                    task_id_to_ok_cnt[task_id] = cnt_ok + 1

        task_id_to_num = {}
        with open(src_dir + '/task_ids.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                task_id = int(row['id'])
                task_id_to_num[task_id] = row['task_no']

        result_by_task_num = {}
        for task_id, cnt in task_id_to_cnt.items():
            cnt_ok = task_id_to_ok_cnt.get(task_id, 0)

            [num, _] = task_id_to_num[task_id].split('-')
            (cur_cnt, cur_cnt_ok) = result_by_task_num.get(num, (0, 0))
            result_by_task_num[num] = (cur_cnt + cnt, cur_cnt_ok + cnt_ok)

        data = []
        diffs = []
        for task_num, (cnt, cnt_ok) in result_by_task_num.items():
            fraction = cnt_ok / cnt if cnt != 0 else 0
            data.append((task_num,round(fraction, 2)))
            diffs.append(round(fraction, 2)) #we get a dictionary /data/ with difficulties as keys and number of tasks as values
        diffs.sort(reverse=True) #and a list with difficulties, sorted by increasing order
        print(data,'сложности задач: сложность:номер задачи')
        data = sorted(data, key=lambda x: x[1], reverse=True)
        return data

    data = get_fraction(file_path)
            #fut_dif = {y: x for x, y in data.iteritems()} #номера задач как ключи и сложности как значения
            #dict_sor_diff = sorted(data.items(), reverse=True)
            #print(dict_sor_diff,'the sorted dictionary')
            #print(diffs,'list of difficulties in a decreasing order')
    #print(data.keys())
    diffs=[]
    print(data,"look here")
    for i in data:
        diffs.append(i[1])

    print(diffs)
    def make_scores(diffs,data):
        new_temp = []
        diffs.sort(reverse=True)
        #print(diffs)
        for i in data:
            new_temp.append(i[0])
            #print(data[i])
            #print(new_temp)
        new_temp = list(map(int,new_temp))
        #print(new_temp)

        i = 1
        new_scores = [0] * len(diffs)
        for j in new_temp:
            new_scores[j-1] = i
            i += 1
            #print(new_scores)
        return new_scores #самая легкая задача - та, с макс дробью сложности. ей надо дать 1 балл, та которая с максимальной - надо дать 8 баллов)

    #once we have the difficulties, we need to sort them in a decreasing order and assign scores
    f_scores = make_scores(diffs,get_fraction(file_path))
    #dif_temp = sorted(diff.items(), key=lambda x: x[1], reverse=True)
    #print(f_scores) #new scores!!
    print(f_scores)

    def scale(f_scores,n,scaling):
        new_results = []
        for i in range(len(scaling)):
            new_results.append(f_scores[i % n] * scaling[i])
        #print(len(new_results))
        return new_results
    #print(len(nums))

    def sum_up(nums,n): #summing up scores for each 18 tasks for every person
        res_sums = []
        j = 0
        while j != len(nums):
            res_sums.append(sum(nums[j:j + n]))
            j += n
        res_sums.sort(reverse=True)
        #print(set(res_sums),'screenshot #3')
        #time.sleep(20)
        return res_sums

    def count_diplomas(p,num):
        n = math.ceil(len(num) * p/100) # we count how many participants should receive the diplomas
        new_all = num[:n+1]
        #print(num[n+2])
        j = new_all[-1]
        while num[n+1] == num[n]:
            n -= 1
        #print(j)
        return n #no of diplomas

    new_results = scale(f_scores,n,scaling)
    res = sum_up(new_results, n)
    new_dipl = count_diplomas(25,res)
    old_res = sum_up(nums, n)
    old_dipl = count_diplomas(25,old_res)
    print('Новое колво дипломов',new_dipl)
    print('Старое колво дипломов',old_dipl)
    #print('Нулевое приближение ',f_scores)
    #total_dipl = count_diplomas(p,sum_up(scale(get_fraction(file_path),n,scaling),n)) # считаем дипломы для новых скоров собрав все функции
    #print(total_dipl)

    def optimize(n,new_scores,p,scaling,iterations,diffs):
        scores = new_scores
        def check_up(try_scor,j,diffs):
            cnt = 0
            for i in range(len(try_scor)):
                #print(i,j)
                #print(diffs[i],diffs[j])
                if diffs[i] < diffs[j]:
                #    print(try_scor[i],try_scor[j])
                    if try_scor[i] > try_scor[j]:
                #        print('ok')
                        cnt +=1
                    #print(diffs[i],diffs[j],try_scor[i],try_scor[i])
                elif diffs[i] > diffs[j]:
                    if try_scor[i] < try_scor[j]:
                 #       print('ok')
                        cnt += 1
                elif diffs[i] == diffs[j]:
                    if try_scor[i] == try_scor[j]:
                  #      print('ok')
                        cnt += 1
                else:
                    cnt = 0

            if cnt == len(try_scor):
                return True
                #if abs(diffs[i] - diffs[j]) <= 0.01 and abs(try_scor[i] - try_scor[j]) <= 1:
                #    return True
            else:
                return False
        def shift(new_scores,j): # функция добавляющая и отнимающая по одному баллу за случайное задание
            sc1,sc2 = new_scores.copy(),new_scores.copy()
            sc1[j] += 1
            if sc2[j] != 1:
                sc2[j] -= 1
            else:
                sc2[j] = sc2[j]
            sc0 = new_scores
            if random.randint(0,100) >= 90:
                sc1[j] = int((sc1[j]-1)*1.5)
            print(sc0,sc1,sc2)

            if not(check_up(sc1,j,diffs)):
                sc1 = sc0
            if not(check_up(sc2, j, diffs)):
                sc2 = sc0

            return sc0,sc1,sc2
        for k in range(iterations):
            print("\n")
            print('номер итерации',k+1)
            print(scores,'текущие скоры, которые дают максимальное число дипломов')
            i = random.choice(range(0, n, 1))
            dct = {}
            s0,s1,s2 =shift(scores,i)
            cur_dipl0 = count_diplomas(p, sum_up(scale(s0, n, scaling), n))
            dct[cur_dipl0] = s0
            cur_dipl1 = count_diplomas(p, sum_up(scale(s1, n, scaling), n))
            dct[cur_dipl1] = s1
            cur_dipl2 = count_diplomas(p, sum_up(scale(s2, n, scaling), n))
            dct[cur_dipl2] = s2
            scores = dct[max(cur_dipl0,cur_dipl1,cur_dipl2)]
            print(max(cur_dipl0,cur_dipl1,cur_dipl2), 'текущий максимум дипломов')
        return scores
    optimize(n,f_scores,p,scaling,iter,diffs)

init(input(),input())