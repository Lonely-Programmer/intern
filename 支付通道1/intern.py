import numpy as np
import random
import sys

class Account:    #一个Account代表一个账户
    def __init__(self,k,value = [0,0,0,0,0,0]):
        self.money = 0    #余额
        self.user = -1    #该账户属于哪个用户
        self.visited = 0    #bfs标记
        self.prev = None    #bfs路径记录

class Data:    #网络结构
    def __init__(self,k,l,ns):    #初始化
        self.dat = []    #网络数据，dat[i]表示相应层，dat[i]内各元素表示该层所有账户
        self.level = l    #网络层数l
        self.k = k    #每个通道的账户数k
        self.user_num = ns    #用户数量
        self.route = []    #路由表，route[i]表示第i个用户的所有账户坐标

        #构建网络结构(self.dat)
        cnt = k
        for i in range(l):
            tmp = []
            for j in range(cnt):
                tmp.append(Account(k))
            self.dat.append(tmp)
            cnt *= k

        #复制用户
        account_num = [1] * ns
        user_tmp = list(range(ns))
        while len(user_tmp) < len(self.dat[-1]):
            tmp = random.choice(user_tmp)
            account_num[tmp] += 1
            user_tmp.append(tmp)

        #通道划分
        accounts = []
        for i in range(len(self.dat[-2])):
            accounts.append([])
        for i in range(ns):
            self.route.append([])
        idx = np.argsort(account_num)
        for i in range(len(idx)-1,-1,-1):
            for j in range(account_num[idx[i]]):
                while True:
                    tmp = random.randint(0,len(self.dat[-2])-1)
                    if len(accounts[tmp]) < self.k and not(idx[i] in accounts[tmp]):
                        accounts[tmp].append(idx[i])
                        break

        #每个通道shuffle
        for i in range(len(accounts)):
            random.shuffle(accounts[i])

        #存储，每个账户属于哪个用户，每个用户有哪些账户
        cnt = 0
        for i in accounts:
            for j in i:
                self.dat[-1][cnt].user = j
                self.route[j].append(self.dec_to_k(cnt))
                cnt += 1

        #读取数据并设定初始余额
        self.read_data()
        #print(self.route[self.dat[-1][-1].user])
        #print(self.get_adjacent_person(self.dat[-1][-1].user))

    def read_data(self):
        #底层
        values = np.load("data/data.npy")
        #values.sort()
        #values = values[0:self.k ** self.level]
        random.shuffle(values)
        for i in range(len(self.dat[self.level-1])):
            if i % self.k == 0:
                continue
            self.dat[self.level-1][i].money = values[i]

        #其余层
        for i in range(self.level-1,0,-1):
            for j in range(0, len(self.dat[i]), self.k):
                sum_tmp = 0
                for k in range(j+1, j+self.k):
                    sum_tmp += self.dat[i][k].money
                self.dat[i][j].money = sum_tmp + 0
                self.dat[i-1][int(j/self.k)].money = self.dat[i][j].money + 0
                self.dat[i-1][int(j/self.k)].user = self.dat[i][j].user    #设定其余层账户属于的用户

        #将路由表扩展到所有层
        for i in self.route:
            for j in i:
                tmp = j
                if len(tmp) < self.level:
                    break
                while len(tmp) > 1 and tmp[-1] == 0:
                    tmp = tmp[0:-1]
                    i.append(tmp)

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
            ans[idx] = x % self.k
            idx -= 1
            x = int(x / self.k)
        return tuple(ans)

    def k_to_dec(self,pos):    #用户坐标转编号
        tmp = 1
        ans = 0
        for i in range(len(pos)-1,-1,-1):
            ans += tmp * pos[i]
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
        for i in self.route[user]:
            for j in range(self.k):
                if j == i[-1]:
                    continue
                tmp.append(i[0:-1]+(j,))
        for i in tmp:
            ans.append(self.get_account(i).user)
        ans = list(set(ans))
        return ans

    def is_adjacent_person(self,user1,user2):    #判断两个用户是否相邻
        if user2 in self.get_adjacent_person(user1):
            return True
        return False

    def is_adjacent_account(self,x,y):    #判断两个账户是否相邻
        if x[0:-1] == y[0:-1] and x[-1] != y[-1]:
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
        #print(self.route[curr_user])
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

    def bfs(self,pos1,pos2):    #bfs寻找两坐标的最短路径
        
        
        for i in self.dat:
            for j in i:
                j.visited = 0
        queue = [pos1]
        self.get_person(pos1).visited = 1
        
        while len(queue) > 0:
            #print(queue)
            tmp = list(queue[0])
            curr = self.get_person(tmp).visited

            if tuple(tmp) == pos2:    #找到目标用户
                #print(curr)
                #break
                del queue[0]
                continue
            
            if tmp[-1] == 0 and len(tmp) > 1 and self.get_person(tuple(tmp[0:-1])).visited == 0:    #如果该点是0号点，则可以往上一层
                self.get_person(tuple(tmp[0:-1])).visited = curr + 1
                self.get_person(tuple(tmp[0:-1])).prev = tuple(tmp)
                queue.append(tuple(tmp[0:-1]))

            if len(tmp) < self.level:    #向下一层
                tmp2 = tmp + [0]
                for i in range(self.k):
                    tmp2[-1] = i
                    new_pos = tuple(tmp2)
                    if self.get_person(new_pos).visited == 0:
                        self.get_person(new_pos).visited = curr
                        self.get_person(new_pos).prev = tuple(tmp)
                        queue.append(new_pos)

            tmp2 = tuple(tmp)
            for i in range(self.k):    #向同组用户发出请求
                tmp[-1] = i
                new_pos = tuple(tmp)
                if self.get_person(new_pos).visited == 0:    #
                    self.get_person(new_pos).visited = curr + 1
                    self.get_person(new_pos).prev = tuple(tmp2)
                    queue.append(new_pos)
            del queue[0]

        ans = [pos2]
        tmp = pos2
        while tmp != pos1:    #返回路径
            tmp = self.get_person(tmp).prev
            ans.insert(0,tmp)

        return ans

    
    def show(self):
        for i in range(100):
            print(i, self.dat[self.level-1][i].money)

class Test:
    def __init__(self,k,l,ns):
        self.network = Data(k,l,ns)
        
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
                if flag[0] == "pareto":
                    value = self.pareto(flag[1],flag[2])
                elif flag[0] == "uniform":
                    value = self.uniform(flag[1],flag[2])
                if self.is_valid(start_person,value) :
                    break
            result = self.network.transaction(start_person,destn,value)
            if result[0] >= 0:
                success += 1
                length += result[0]
            message += result[1]
        
        length /= success
        message /= n
        return (success,length,message)
        #print(success,n,length,message)

class Demo:
    def __init__(self):
        self.test = None

    def average(self,k,l,ns,n,flag):
        success = 0
        length = 0
        message = 0
        for i in range(n):
            self.test = Test(k,l,ns)
            result = self.test.transaction(5000,flag)
            success += result[0]
            length += result[1]
            message += result[2]

        success /= n
        length /= n
        message /= n
        return (success,length,message)

    def k_and_l(self,flag=("pareto",1.1,1000)):
        k = [4,5,6]
        l = [[2,3,4,5],[2,3,4],[2,3,4]]
        for i in range(3):
            tmp_k = k[i]
            for tmp_l in l[i]:
                print("k = ",tmp_k," l = ",tmp_l,"   ",self.average(tmp_k,tmp_l,tmp_k**tmp_l,20,flag))

def main():
    #a = Account(5)
    #print(a.balance)
    #b = Data(6,4,500)
    #print(b.find_way(b.dat[-1][b.k_to_dec((0,1,2,3))].user,(1,2,4,3),5))
    #c = Test(6,4,300)
    #c.transaction(5000)
    test = [("uniform",0,2000),("pareto",1.16,500),("pareto",1.16,1000),("pareto",1.16,1500),("pareto",1.1,1000),("pareto",1.16,1000),("pareto",1.25,1000)]
    d = Demo()
    for i in test:
        print(i)
        d.k_and_l(i)
        print()

main()

