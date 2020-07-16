import numpy as np
import random
import time

class Account:    #一个Account代表一个账户
    def __init__(self,k,value = [0,0,0,0,0,0]):
        self.money = 0    #余额
        self.user = -1    #该账户属于哪个用户
        self.visited = 0    #bfs标记
        self.prev = None    #bfs路径记录
        self.is_supervisor = False    #是否是监督者

class Data:    #网络结构
    def __init__(self,k,l,rs):    #初始化
        self.dat = []    #网络数据，dat[i]表示相应层，dat[i]内各元素表示该层所有账户
        self.level = l    #网络层数l
        self.k = k    #每个通道的账户数k
        self.user_num = 67149    #用户数量
        self.account_num = int(self.user_num * (1 + rs) + 0.5)    #底层账户数量
        self.route = []    #路由表，route[i]表示第i个用户的所有账户坐标
        self.low_bound = k
        self.high_bound = 2500
        self.supervisor = []
        self.original_money = 0
        self.actual_money = 0

        #构建网络结构(self.dat)
        cnt = k
        cnt2 = 1
        for i in range(l):
            tmp = []
            tmp2 = []
            for j in range(cnt):
                tmp.append(Account(k))
            for j in range(cnt2):
                tmp2.append(0)
                
            self.dat.append(tmp)
            self.supervisor.append(tmp2)
            if i == l - 2:
                cnt *= self.high_bound
                cnt2 *= k
            else:
                cnt *= k
                cnt2 *= k

        for i in range(self.user_num):
            self.route.append([])

        accounts = list(np.load("data/group_6561.npy", allow_pickle=True))

        #存储，每个账户属于哪个用户，每个用户有哪些账户
        cnt = 0
        for i in accounts:
            for j in range(self.high_bound):
                if j < len(i):
                    self.dat[-1][cnt].user = i[j]
                    self.route[i[j]].append(self.dec_to_k(cnt))
                    cnt += 1
                else:
                    cnt += (self.high_bound - j)
                    break

        #读取数据并设定初始余额
        self.read_data()

    def read_data(self):
        #底层
        values = np.load("data/data2.npy")
        values = values[0:self.user_num]

        for i in range(len(self.route)):
            self.original_money += values[i]

        #将钱分配到一个用户的所有账户，金额一致
        for i in range(len(self.route)):
            for j in range(len(self.route[i])):
                self.get_account(self.route[i][j]).money = values[i]
                #print([i][j],values[i])

        for i in range(0,len(self.dat[-1]),self.high_bound):
            tmp = 0
            idx = i
            for j in range(self.high_bound):
                if self.dat[-1][i+j].user == -1:
                    break
                if self.dat[-1][i+j].money > tmp:
                    idx = i + j
                    tmp = self.dat[-1][i+j].money

            self.dat[-1][idx].is_supervisor = True
            self.supervisor[-1][int(i/self.high_bound)] = idx - i    #设置底层监督者
            
        #其余层
        for i in range(self.level-1,0,-1):
            if i == self.level - 1:
                tmp = self.high_bound
            else:
                tmp = self.k
            for j in range(0, len(self.dat[i]), tmp):
                sum_tmp = 0
                for k in range(j, j+tmp):
                    if self.dat[i][k].is_supervisor == False:
                        sum_tmp += self.dat[i][k].money
                self.dat[i][j+self.supervisor[i][int(j/tmp)]].money = sum_tmp + 0
                self.dat[i-1][int(j/tmp)].money = self.dat[i][j+self.supervisor[i][int(j/tmp)]].money + 0
                self.dat[i-1][int(j/tmp)].user = self.dat[i][j+self.supervisor[i][int(j/tmp)]].user    #设定其余层账户属于的用户
                
            for j in range(0,len(self.dat[i-1]),self.k):
                tmp = 0
                idx = j
                for k in range(self.k):
                    if self.dat[i-1][j+k].user != -1 and self.dat[i-1][j+k].money > tmp:
                        idx = j + k
                        tmp = self.dat[i-1][j+k].money
                self.dat[i-1][idx].is_supervisor = True
                self.supervisor[i-1][int(j/self.k)] = idx - j    #设置监督者
                
        #将路由表扩展到所有层
        for i in self.route:
            for j in i:
                tmp = j
                if len(tmp) < self.level:
                    break
                while len(tmp) > 1 and self.get_account(tmp).is_supervisor == True:
                    tmp = tmp[0:-1]
                    i.append(tmp)

        for i in self.dat:
            for j in i:
                if j.user == -1:
                    break
                self.actual_money += j.money

    def pos_dist(self,x,y):    #坐标距离
        if x == y:
            return 0
        for i in range(self.level):
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

    def dec_to_k(self,x):    #用户编号转坐标
        ans = [0] * self.level
        idx = self.level - 1
        while x > 0:
            if idx == self.level - 1:
                ans[idx] = x % self.high_bound
                idx -= 1
                x = int(x / self.high_bound)
            else:
                ans[idx] = x % self.k
                idx -= 1
                x = int(x / self.k)
        return tuple(ans)

    def k_to_dec(self,pos):    #用户坐标转编号
        tmp = 1
        ans = 0
        for i in range(len(pos)-1,-1,-1):
            ans += tmp * pos[i]
            if len(pos) == self.level and i == len(pos) - 1:
                tmp *= self.high_bound
            else:
                tmp *= self.k
        return ans

    def get_account(self,pos):     #通过坐标返回用户
        ans = self.dat[len(pos)-1]
        idx = self.k_to_dec(pos)
        ans = ans[idx]
        return ans

    def get_adjacent_person(self,user):    #返回相邻用户
        tmp = []
        ans = []
        #print(self.route[user])
        for i in self.route[user]:
            if len(i) == self.level:
                up = self.high_bound
            else:
                up = self.k
            for j in range(up):
                if j == i[-1]:
                    continue
                tmp2 = i[0:-1]+(j,)
                if self.get_account(tmp2).user == -1:
                    break
                tmp.append(tmp2)

        #print(tmp)
        for i in tmp:
            if self.get_account(i).user != -1:
                ans.append(self.get_account(i).user)
        ans = list(set(ans))
        return ans

    def is_adjacent_person(self,user1,user2):    #判断两个用户是否相邻
        if user2 in self.get_adjacent_person(user1):
            return True
        return False

    def is_adjacent_account(self,x,y):    #判断两个账户是否相邻
        if self.get_account(x).user != -1 and self.get_account(y).user != -1 and x[0:-1] == y[0:-1] and x[-1] != y[-1]:
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
    def __init__(self,k,l,rs,fixed = False):
        if fixed == True:
            random.seed(random.randint(0,100000000))    #初始化随机种子
        self.network = Data(k,l,rs)
        self.trans_dat = np.load("data/trans_dat.npy")
        if fixed == True:
            random.seed(int((k ** l) * (1000 * rs)))    #固定随机种子
            random.seed(time.time())
        
    def pareto(self,k,mean):
        xmin = mean * (k-1) / k
        s = (np.random.pareto(k) + 1) * xmin
        return s

    def uniform(self,low,high):
        return random.uniform(low,high)

    def random_pos(self):
        person = random.randint(0,self.network.user_num-1)
        account = random.choice(self.network.route[person])
        return account

    def is_valid(self,start_person,value):
        for i in self.network.route[start_person]:
            if self.network.get_account(i).money > value:
                return True
        return False

    def transaction(self,n,flag):
        success = 0
        length = 0
        message = 0

        for i in range(n):
            while True:
                start_person = random.randint(0,self.network.user_num-1)
                destn = self.random_pos()
                if flag[0] == "data":
                    value = random.choice(self.trans_dat)[2] * 100000
                elif flag[0] == "pareto":
                    value = self.pareto(flag[1],flag[2])
                elif flag[0] == "uniform":
                    value = self.uniform(flag[1],flag[2])
                if self.is_valid(start_person,value):
                    break
            result = self.network.transaction(start_person,destn,value)
            if result[0] >= 0:
                success += 1
                length += result[0]
                message += result[1]

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

    def average(self,k,l,rs,n,flag):
        success = []
        length = []
        message = []
        for i in range(n):
            self.test = Test(k,l,rs)
            print("zzz")
            result = self.test.transaction(50000,flag)    #transaction number
            success.append(result[0] / 50000)    #transaction number
            length.append(result[1])
            message.append(result[2])

        success_mean = np.mean(success)
        success_var = np.var(success)
        length_mean = np.mean(length)
        length_var = np.var(length)
        message_mean = np.mean(message)
        message_var = np.var(message)
        
        return (success_mean,success_var,length_mean,length_var,message_mean,message_var)

    def scalability(self,k,l,rs,n,flag):
        ans = [0] * 5
        show = [30000,50000,100000,150000,200000,200100]
        curr = 0
        for i in range(n):
            self.test = Test(k,l,rs,True)
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
        return ans

    def kl_test(self,flag=("data",)):
        k = [9,81]
        l = [[5],[3]]
        r = [0]
        for i in range(len(k)):
            tmp_k = k[i]
            for tmp_l in l[i]:
                for tmp_r in r:
                    print("k = ",tmp_k," depth = ",tmp_l-1," rs = ",tmp_r,"   ",self.average(tmp_k,tmp_l,tmp_r,5,flag))

    def rs_test(self,flag=("data",)):
        k = [4,8,64]
        l = [[4],[3],[2]]
        r = [0]
        for i in range(len(k)):
            tmp_k = k[i]
            for tmp_l in l[i]:
                for tmp_r in r:
                    print("k = ",tmp_k," depth = ",tmp_l-1," rs = ",tmp_r,"   ",self.average(tmp_k,tmp_l,tmp_r,1,flag))
    
    def scalability_test(self,flag=("data",)):
        k = [9,81]
        l = [[5],[3]]
        r = [0]
        for i in range(len(k)):
            tmp_k = k[i]
            for tmp_l in l[i]:
                for tmp_r in r:
                    print("k = ",tmp_k," depth = ",tmp_l-1," rs = ",tmp_r,"   ",self.scalability(tmp_k,tmp_l,tmp_r,1,flag))

    def money_test(self):
        k = [16,64]
        l = [[4],[3]]
        r = [0]
        for i in range(len(k)):
            tmp_k = k[i]
            for tmp_l in l[i]:
                for tmp_r in r:
                    self.test = Test(tmp_k,tmp_l,tmp_r)
                    tmp = self.test.money_compare()
                    money1 = tmp[0]
                    money2 = tmp[1]
                    print("k = ",tmp_k," depth = ",tmp_l-1," rs = ",tmp_r,"   money of supervisors: ",money1," data: ",money2)

    def stablization_test(self):
        k = [16,64]
        l = [[4],[3]]
        r = [0]
        for i in range(len(k)):
            tmp_k = k[i]
            for tmp_l in l[i]:
                for tmp_r in r:
                    ans_random = []
                    for j in range(1):
                        self.test = Test(tmp_k,tmp_l,tmp_r)
                        ans_random.append(self.test.network.get_stabilization())
                        
                    ans_random_mean = np.mean(ans_random)
                    ans_random_var = np.var(ans_random)

                    ans = (ans_random_mean,ans_random_var)
                    print("k = ",tmp_k," depth = ",tmp_l-1," rs = ",tmp_r,"   M: ",ans)
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
    #b = Data(5,5,0)
    #print(b.dec_to_k(1200))
    #print(b.k_to_dec((4,4,0,9)))
    #print(b.transaction(b.dat[-1][b.k_to_dec((0,1,2,3))].user,(1,2,4,3),0))
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
        #print(i)
        #d.kl_test(i)
        #d.rs_test(i)
        #d.money_test()
        d.scalability_test(i)
        #d.stablization_test()
        #print()

main()

