import numpy as np
import random
import time

class Account:    #一个Account代表一个账户
    def __init__(self):
        self.money = 0    #余额
        self.user = -1    #该账户属于哪个用户

class Passage:
    def __init__(self,n=0):
        self.accounts = []
        self.children = []
        self.parent = None
        self.pos = ()
        for i in range(n):
            self.accounts.append(Account())

class Data:    #网络结构
    def __init__(self,d):    #初始化
        self.dat = []    #网络数据，dat[i]表示相应层，dat[i]内各元素表示该层所有账户
        self.user_num = 67149    #用户数量
        self.route = []    #路由表，route[i]表示第i个用户的所有账户坐标
        self.supervisor = []
        self.original_money = 0
        self.actual_money = 0
        self.d = d
        self.isolated_passages = []
        self.available_users = []
        self.rec = 0

        #读取数据并设定初始余额
        self.read_data()

    def read_data(self):
        tmp = np.load("data/data_" + str(self.d) + ".npy",allow_pickle=True)
        values = np.load("data/data2.npy")
        passages = tmp[0]
        passage_edges = tmp[1]
        isolated_passages = tmp[2]
        self.isolated_passages = isolated_passages

        for i in passages:
            self.dat.append(Passage(len(i)))
            for j in range(len(i)):
                self.dat[-1].accounts[j].user = i[j]
                self.dat[-1].accounts[j].money = values[i[j]]
            
        for i in passage_edges:
            start = i[0]
            end = i[1]
            self.dat[start].children.append(end)
            self.dat[end].parent = start

        for i in range(100000):
            self.route.append([])
        for i in range(len(self.dat)):
            for j in range(len(self.dat[i].accounts)):
                self.route[self.dat[i].accounts[j].user].append((i,j))

        for i in range(len(self.dat)):
            for j in range(len(self.dat[i].children)):
                self.dat[self.dat[i].children[j]].pos = self.dat[i].pos + (j,)

        for i in range(100000):
            if len(self.route[i]) > 1 or (len(self.route[i]) == 1 and self.route[i][0][0] not in self.isolated_passages):
                self.available_users.append(i)
        #print(len(self.available_users))
        return
        for i in range(10):
            print(self.route[i])

    def pos_dist(self,x,y):    #坐标距离
        x = self.dec_to_k(x[0])+(x[1],)
        y = self.dec_to_k(y[0])+(y[1],)
        if x == y:
            return 0
        for i in range(100):
            if i >= len(x) or i >= len(y):
                break
            if x[i] != y[i]:
                break
        return len(x) + len(y) - 2 * i

    def super_pos_dist(self,user,dest):    #考虑同一用户不同账户的坐标距离
        dist = 10000000
        for i in self.route[user]:
            tmp = self.pos_dist(i,dest)
            if tmp < dist:
                dist = tmp
        return dist

    def dec_to_k(self,x):    #通道编号转坐标
        return self.dat[x].pos

    def k_to_dec(self,pos):    #通道坐标转编号
        ans = 0
        for i in pos:
            ans = self.dat[ans].children[i]
        return ans

    def get_account(self,pos):     #通过坐标返回用户
        ans = self.dat[pos[0]].accounts[pos[1]]
        return ans

    def get_adjacent_person(self,user):    #返回相邻用户
        tmp = []
        ans = []
        #print(self.route[user])
        for i in self.route[user]:
            for j in range(len(self.dat[i[0]].accounts)):
                if j == i[1]:
                    continue
                tmp2 = (i[0],j)
                tmp.append(tmp2)

        #print(tmp)
        for i in tmp:
            if self.get_account(i).user != -1:
                ans.append(self.get_account(i).user)
        ans = list(set(ans))
        return ans

    def is_isolated_user(self,user):
        for i in self.route[user]:
            if i[0] not in self.isolated_passages:
                return False
        return True

    def is_isolated_passage(self,passage):
        return passage in self.isolated_passages

    def is_adjacent_person(self,user1,user2):    #判断两个用户是否相邻
        if user2 in self.get_adjacent_person(user1):
            return True
        return False

    def is_adjacent_account(self,x,y):    #判断两个账户是否相邻
        if self.get_account(x).user != -1 and self.get_account(y).user != -1 and x[0] == y[0] and x[1] != y[1]:
            return True
        return False

    def get_adjacent_account(self,user1,user2):    #返回相邻用户可直接交易的账户对集合
        ans = []
        for i in self.route[user1]:
            for j in self.route[user2]:
                if self.is_adjacent_account(i,j):
                    ans.append((i,j))
        random.shuffle(ans)
        return ans

    def greedy(self,prev_user,curr_user,destn,value):    #message传递递归
        if self.rec > 50:
            #print("a")
            return (-1,0,[],[])
        if destn in self.route[curr_user]:    #目标已经是自己的账户之一，则结束            
            return (0, 0,[],[])
        
        if prev_user >= 0 and not(self.is_adjacent_person(prev_user,curr_user)):    #前一个用户与自己不相邻，返回失败
            return (-1,0,[],[])

        choices = self.get_adjacent_person(curr_user)    #候选用户
        dist_threshold = self.super_pos_dist(curr_user,destn)    #自己到目标的距离
        dist = []    #各候选用户的距离
        for i in choices:
            dist.append(self.super_pos_dist(i,destn))
        idx = np.argsort(dist)    #距离下标排序

        message = 0    #消息条数
               
        for i in idx:    #遍历所有可抵达的距离更短的用户
            if dist[i] >= dist_threshold:    #判断是否大于自身距离
                break
            tmp = self.get_adjacent_account(curr_user,choices[i])
            for j in tmp:    #遍历所有可以和第i个用户转账的账户
                if self.get_account(j[0]).money < value:
                    if self.rec > 50:
                        #print("b")
                        break
                    continue
                message += 1    #发送消息
                ans = self.greedy(curr_user,choices[i],destn,value)    #请求下一个用户
                message += ans[1]    #继承下一用户的消息数量
                message += 1    #接收消息
                

                if ans[0] >= 0:    #若成功
                    self.get_account(j[0]).money -= value    #转钱
                    self.get_account(j[1]).money += value
                    #print(j[0],"->",j[1])
                    return (ans[0]+1, message,[choices[i],]+ans[2],[(j[0])]+[(j[1])]+ans[3])
            
        return (-1,message,())    #失败

    def transaction(self,start_person,destn,value):    #模拟实际路径搜索
        tmp = self.greedy(-1,start_person,destn,value)
        return tmp

    def total_money(self):
        return (self.actual_money,self.original_money)
    
    def get_M(self):
        M = 0
        for i in range(0,len(self.dat[-1]),self.high_bound):
            tmp = 0
            for j in range(self.high_bound):
                if self.dat[-1][i+j].user != -1:
                    tmp += 1
                else:
                    if tmp > M:
                        M = tmp
                        break
        return M

    def get_stabilization(self):
        ans = 0
        for i in range(0,len(self.dat[-1]),self.high_bound):
            tmp = 0
            for j in range(self.high_bound):
                if self.dat[-1][i+j].user != -1:
                    tmp += 1
                else:
                    ans += (tmp * (tmp - 1))
                    break
        ans += (self.k ** self.level - self.k)
        return ans

class Test:
    def __init__(self,k,n):
        self.network = Data(k)
        self.trans_dat = []
        z = random.sample(list(range(20)),5)
        #print(n)
        for i in z:
            with open("data/sampleTr-" + str(i) + ".txt") as f:
                for line in f:
                    tmp = line.split()
                    tmp1 = float(tmp[0])
                    tmp2 = int(tmp[1])
                    tmp3 = int(tmp[2])
                    self.trans_dat.append((tmp1,tmp2,tmp3))

    def is_valid(self,start_person,value):
        for i in self.network.route[start_person]:
            if self.network.get_account(i).money > value:
                return True
        return False

    def transaction(self,n,flag):
        success = 0
        length = 0
        message = 0
        total = 0
        i = 0
        delay = []
        retry_flag = False

        while True:
            i %= len(self.trans_dat) - 100
            #print(len(self.trans_dat) - 100,delay)
            if flag[0] == "data":
                if len(delay) > 0 and (total >= delay[0][4] or total >= n):
                    value = delay[0][0]
                    start_person = delay[0][1]
                    destn = delay[0][2]
                    retry_flag = True
                else:
                    retry_flag = False
                    value = self.trans_dat[i][0]
                    failure = 0
                    while True:
                        start_person = random.randint(0,100000-1)
                        #print(1)
                        if len(self.network.route[start_person]) > 0 and not(self.network.is_isolated_user(start_person)):   #and self.is_valid(start_person,value) 
                            break
                        failure += 1
                        if failure > 1000:
                            failure = 0
                            i += 1
                            value = self.trans_dat[i][0]
                    #print(failure)
                    while True:
                        destn = random.randint(0,100000-1)
                        #print(2)
                        if len(self.network.route[destn]) > 0:
                            destn = random.choice(self.network.route[destn])
                            if not(self.network.is_isolated_passage(destn[0])):
                                break

            #print(total+1,value,start_person,destn)
            result = self.network.transaction(start_person,destn,value)
            if result[0] >= 0:
                success += 1
                length += result[0]
                message += result[1]
                if retry_flag:
                    del delay[0]
                else:
                    i += 1
                    total += 1
            else:
                if retry_flag:
                    if delay[0][3] > 1:
                        delay.append((value,start_person,destn,delay[0][3]-1,total+2000))
                    else:
                        pass
                    del delay[0]
                else:
                    delay.append((value,start_person,destn,2-1,total+2000))
                    total += 1
            
            
            if total >= n and len(delay) == 0:
            #if total >= n:
                break

##            if (total+1) % 1000 == 0:
##                print(total+1,i+1)

        if success != 0:
            length /= success
            message /= success
        else:
            length = -1
            message = -1
        return (success,length,message)
    
    def money_compare(self):
        return self.network.total_money()

class Demo:
    def __init__(self):
        self.test = None

    def average(self,k,n,flag):
        success = []
        length = []
        message = []
        for i in range(n):
            self.test = Test(k,i)
            result = self.test.transaction(200,flag)    #transaction number
            success.append(result[0] / 200)    #transaction number
            length.append(result[1])
            message.append(result[2])

            print(result)

        success_mean = np.mean(success)
        success_var = np.var(success)
        length_mean = np.mean(length)
        length_var = np.var(length)
        message_mean = np.mean(message)
        message_var = np.var(message)
        
        return (success_mean,success_var,length_mean,length_var,message_mean,message_var)

    def scalability(self,k,n,flag):
        f = open("scalability_"+str(k)+"_"+str(random.randint(0,100000))+".txt","w")
        ans = [0] * 5
        show = [30000,50000,100000,150000,200000,200100]
        curr = 0
        self.test = Test(k,n)
        success = 0
        for j in range(0,200000):
            result = self.test.transaction(1,flag)
            success += result[0]
            if j+1  == show[curr]:
                ans[curr] += success
                print(show[curr], success / show[curr])
                curr += 1
                    
        for i in range(len(ans)):
            ans[i] /= n
            ans[i] /= show[i]
        f.write(str(ans))
        f.close()
        return ans

    def kl_test(self,flag=("data",)):
        k = [5,10,29]
        for i in k:
            print("k = ",i,"   ",self.average(i,1,flag))

    def scalability_test(self,flag=("data",)):
        k = [5,6,29]
        for i in k:
            print("k = ",i,"   ",self.scalability(i,1,flag))

    def money_test(self):
        k = [5,6,29]
        
        for i in range(len(k)):
            tmp_k = k[i]
            for tmp_l in l[i]:
                for tmp_r in r:
                    result1 = []
                    result2 = []
                    for z in range(10):
                        self.test = Test(tmp_k,tmp_l,tmp_r)
                        tmp = self.test.money_compare()
                        money1 = tmp[0]
                        money2 = tmp[1]
                        result1.append(money1)
                        result2.append(money2)
                    result = [np.mean(result1),np.var(result1),np.mean(result2),np.var(result2)]
                    print(result1)
                    print(result2)
                    print("k = ",tmp_k," depth = ",tmp_l-1," rs = ",tmp_r,"   money of supervisors,data : ",result)
                    

    def stablization_test(self):
        k = [5,6,29]
        for i in range(len(k)):
            tmp_k = k[i]
            for tmp_l in l[i]:
                for tmp_r in r:
                    ans_random = []
                    for j in range(10):
                        self.test = Test(tmp_k,tmp_l,tmp_r)
                        ans_random.append(self.test.network.get_stabilization())
                        
                    ans_random_mean = np.mean(ans_random)
                    ans_random_var = np.var(ans_random)

                    ans = (ans_random_mean,ans_random_var)
                    print(ans_random)
                    print("k = ",tmp_k," depth = ",tmp_l-1," rs = ",tmp_r,"   s: ",ans)
                    continue

                    person_num = int(2469 * (1 + tmp_r) + 0.5)
                    group_num = tmp_k ** (tmp_l - 1)
                    person_num1 = int(person_num / group_num)
                    person_num2 = person_num1 + 1
                    group_num1 = person_num2 * group_num - person_num
                    group_num2 = person_num - person_num1 * group_num
                    ans_average = (tmp_k ** tmp_l) - tmp_k + person_num1 * (person_num1 - 1) * group_num1 + person_num2 * (person_num2 - 1) * group_num2

                    group_num2 = int((941 * group_num - person_num) / (941 - 2))    #2
                    group_num1 = int((person_num - 2 * group_num) / (941 - 2))    #M
                    remain_person = 2469 - group_num1 * 941 - group_num2 * 2
                    ans_2M1 = (tmp_k ** tmp_l) - tmp_k + group_num1 * (941 * 940) + group_num2 * 2 + remain_person * (remain_person - 1)
                    

                    self.test = Test(tmp_k,tmp_l,tmp_r)
                    M = self.test.network.get_M()
                    group_num2 = int((M * group_num - person_num) / (M - 2))
                    group_num1 = int((person_num - 2 * group_num) / (M - 2))
                    remain_person = 2469 - group_num1 * M - group_num2 * 2
                    ans_2M2 = (tmp_k ** tmp_l) - tmp_k + group_num1 * (M * (M - 1)) + group_num2 * 2 + remain_person * (remain_person - 1)
                    #print(group_num1,group_num2,remain_person)
                    
                    ans = (ans_random_mean,ans_random_var,ans_average,ans_2M1,ans_2M2,M)
                    
                    print("k = ",tmp_k," depth = ",tmp_l-1," rs = ",tmp_r,"   M: ",ans)

def main():
    #random.seed(0)
    #a = Account(5)
    #print(a.balance)
    b = Data(5)
    #print(b.dec_to_k(1200))
    #print(b.k_to_dec((4,4,0,9)))
    #b.isolate_
    #print(b.isolated_passages)
    #print(b.transaction(47570,(290,8),1))
    #return
    #print(b.supervisor)
    #c = Test(6,4,300)
    #c.transaction(5000)

    #print("c  ",b.route[b.get_account((1,0)).user])
    #print("c  ",b.get_account((1,0)).user)
    #print("c  ",b.get_account((1,0,0,0)).user)
    #print("a  ",b.get_adjacent_person(b.get_account((1,0)).user))
    #t = b.get_adjacent_person(b.get_account((1,0)).user)
    #for i in t:
    #    print("b  ",b.route[i])
    #return
    test = [("pareto",1.16,1000)]
    test = [("data",)]
    d = Demo()

    for i in test:
        print(i)
        #d.kl_test(i)
        #d.rs_test(i)
        #d.money_test()
        d.scalability_test(i)
        #d.stablization_test()
        print()

for i in range(3):
    main()

