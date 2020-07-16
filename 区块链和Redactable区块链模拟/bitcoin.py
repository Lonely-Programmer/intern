import random
import zsign
import time
import math

class Tx:    #交易
    class Input:    #交易输入
        def __init__(self):
            self.prev_out_hash = ""    #所使用的txio所在交易的hash值
            self.prev_out_n = -1     #该txio是交易中的第几笔输出
            self.scriptSig = ""    #验证脚本
            #self.script_type = ""
            #self.public_key = ""    #

        def set_data(self,dat):   #(prev_out_hash,prev_out_n)，设置输入信息
            self.prev_out_hash = dat[0]
            self.prev_out_n = dat[1]

        def get_size(self):
            return 4 + len(self.prev_out_hash) + len(self.scriptSig)
   
    class Output:    #交易输出
        def __init__ (self):
            self.value = 0    #输出金额
            #self.scriptPubKey = ""
            self.script = ""    #验证脚本
            self.script_type = ""    #脚本类型

        def set_data(self,dat):   #(value,public_key)，设置输出信息
            self.value = dat[0]
            self.script = dat[1]

        def get_size(self):
            return 4 + len(self.script) + len(self.script_type)
            
    def __init__(self):
        #metadata
        self.hash = zsign.random_hash(256)    #交易hash(id)
        self.ver = 1
        self.vin_sz = 2
        self.vout_sz = 1
        self.lock_time = 0
        self.size = 404
        #input
        self.inputs = []    #交易输入
        #output
        self.outputs = []    #交易输出

    def is_coinbase(self):    #是否是coinbase
        return False

    def get_hash(self):    #返回交易hash(id)
        return self.hash

    def get_input_data(self,n):    #返回第n个输入的数据
        tmp = self.inputs[n]
        return (tmp.prev_out_hash,tmp.prev_out_n,tmp.scriptSig,tmp.public_key)

    def get_output_money(self,n):    #返回第n个输出的金额
        return self.outputs[n].value

    def get_output_key(self,n):    #返回第n个输出的接收者公钥
        return self.outputs[n].public_key

    def set_input(self,dat):   #[(prev_out_hash,prev_out_n),...]，设置输入
        self.inputs = []
        for i in range(len(dat)):
            self.inputs.append(self.Input())
            self.inputs[i].set_data(dat[i])

    def set_output(self,dat):   #[(value,public_key),...]，设置输出
        self.outputs = []
        for i in range(len(dat)):
            self.outputs.append(self.Output())
            self.outputs[i].set_data(dat[i])

    def checksig(self,sig,public_key):    #判断签名是否正确
        return zsign.verify(self.calc_hash(),sig,public_key)

    def checkmultisig(self,M,N,sigs,public_keys):    #判断多重签名
        hash_tmp = self.calc_hash()
        correct = 0
        for i in range(M):
            for j in range(N):
                if zsign.verify(hash_tmp,sigs[i],public_keys[j]):
                    correct += 1
                    break
        if correct >= M:
            return True
        return False

    def exec(self,script):    #执行验证脚本
        op = script.split('\t')    #脚本使用字符串形式存储，用\t分隔
        stack = []
        
        for i in range(len(op)):
##            print(stack)
##            print(op[i])
##            print()
            if op[i] == 'OP_DUP':    #复制栈顶数据
                stack.append(stack[-1])
            elif op[i] == 'OP_HASH160':    #对栈顶数据计算hash160并替换
                #print(type(stack[-1]))
                stack[-1] = zsign.hash160(stack[-1])
                #print('e:',stack[-1],'\n',stack[-2])
            elif op[i] == 'OP_EQUALVERIFY':    #判断栈顶处两个数据是否相等，并删除
                #print('e:',stack[-1],'\n',stack[-2])
                if stack[-1] != stack[-2]:
                    print('EQU!\n')
                    return False
                del stack[-1]
                del stack[-1]
            elif op[i] == 'OP_CHECKSIG':    #用公钥stack[-1]判断签名stack[-2]是否正确
                #公钥和前面要先转化为bytes类型
                if not(self.checksig(bytes(stack[-2], encoding = 'utf-8'),bytes(stack[-1], encoding = 'utf-8'))):
                    print('SIG!\n')
                    return False
                del stack[-1]
                del stack[-1]
            elif op[i] == 'OP_CHECKMULTISIG':    #验证多重签名
                public_keys = []
                sigs = []
                original = 'OP_CHECKMULTISIG'    #生成原始输出脚本
                key_num = int(stack[-1])    #读取总签名个数N
                original = str(key_num) + '\t' + original
                del stack[-1]
                for j in range(key_num):    #读入公钥
                    public_keys.append(bytes(stack[-1], encoding = 'utf-8'))
                    original = stack[-1] + '\t' + original
                    del stack[-1]
                sig_num = int(stack[-1])    #读取最少签名数M
                original = str(sig_num) + '\t' + original
                del stack[-1]
                for j in range(sig_num):    #读入签名
                    sigs.append(bytes(stack[-1], encoding = 'utf-8'))
                    del stack[-1]
                if not(self.checkmultisig(sig_num,key_num,sigs,public_keys)):    #验证
                    print('MULTISIG!\n')
                    return False
                stack.append(original)
            elif op[i] == 'OP_0':    #占位符，无操作
                continue
            else:    #是操作数，直接进栈
                stack.append(op[i])
        if len(stack) > 0:    #脚本不完整，验证失败
            return False
        return True    #验证成功

    def clear_input_script(self):    #清除输入中的脚本，用于签名前
        backup = []
        for i in range(len(self.inputs)):
            backup.append(self.inputs[i].scriptSig)
            self.inputs[i].scriptSig = ''
        return backup

    def restore_input_script(self,backup):    #恢复输入中的脚本，用于签名后
        for i in range(len(self.inputs)):
            self.inputs[i].scriptSig = backup[i]

    def calc_hash(self):    #计算自身的hash值
        #print('sha:',zsign.sha(zsign.to_str(self)))
        #print('to_str:',zsign.to_str(self),'\n')
        
        return zsign.hash160(zsign.to_str(self))

    def output_script_gen(self,output_public_key,script_type,M=None,N=None):
        #生成输出的验证脚本，需要传入：接收方的公钥、脚本类型
        if script_type == 'pay-to-public-key-hash':    #p2sh
            tmp = zsign.hash160(str(output_public_key,encoding='utf-8'))    #计算hash前将公钥转为str
            #print('sign key:',output_public_key,'\n',tmp,'\n')
            ans = 'OP_DUP\tOP_HASH160\t' + tmp + '\tOP_EQUALVERIFY\tOP_CHECKSIG'
            return ans
        if script_type == 'pay-to-public-key':    #p2pk
            ans = str(output_public_key,encoding='utf-8') + '\tOP_CHECKSIG'
            return ans
        if script_type == 'pay-to-script-hash':    #p2sh，此时公钥为列表
            ans = ''
            ans = ans + str(M) + '\t'
            for i in range(N):
                #print(output_public_key)
                ans = ans + str(output_public_key[i],encoding='utf-8') + '\t'
            ans = ans + str(N) + '\tOP_CHECKMULTISIG'
            ans = 'OP_HASH160\t' + zsign.hash160(ans) + '\tOP_EQUALVERIFY'
            return ans

    def input_script_gen(self,private_key,public_key,script_type,output_script,input_idx,M=None,N=None):
        #生成输入的验证脚本，需要传入：交易生成者的私钥、公钥、脚本类型、使用的txio的输出脚本、
        #自己是第几个输入
        if script_type == 'nothing':    #初始金额生成用
            return 'nothing'
        if script_type == 'pay-to-public-key-hash':    #p2pkh
            backup = self.clear_input_script()    #清除输入脚本
            #self.inputs[input_idx].scriptSig = output_script    #需要签名的那个输入赋值
            sig = zsign.sign(self.calc_hash(),private_key)    #生成签名
            self.restore_input_script(backup)    #恢复输入脚本
            return str(sig, encoding='utf-8') + '\t' + str(public_key, encoding='utf-8')    #返回签名（转为str）
        if script_type == 'pay-to-public-key':    #p2pk
            backup = self.clear_input_script()    #清除输入脚本
            #self.inputs[input_idx].scriptSig = output_script    #需要签名的那个输入赋值
            sig = zsign.sign(self.calc_hash(),private_key)    #生成签名
            self.restore_input_script(backup)    #恢复输入脚本
            return str(sig, encoding='utf-8')    #返回签名（转为str）
        if script_type == 'pay-to-script-hash':    #p2sh，此时私钥和公钥为列表
            backup = self.clear_input_script()    #清除输入脚本
            #self.inputs[input_idx].scriptSig = output_script    #需要签名的那个输入赋值
            ans = ''
            for i in range(M):
                sig = zsign.sign(self.calc_hash(),private_key[i])    #生成签名
                ans = ans + str(sig, encoding='utf-8') + '\t'
            ans = ans + str(M) + '\t'
            for i in range(N):
                ans = ans + str(public_key[i], encoding='utf-8') + '\t'
            ans = ans + str(N) + '\tOP_CHECKMULTISIG'
            self.restore_input_script(backup)    #恢复输入脚本
            return ans    #返回签名（转为str）

    def sign(self,private_key,public_key,prev_outs,script_types,M=None,N=None):
        #对脚本进行签名，需要传入：交易生成者的私钥、公钥、[用到的txio]、[脚本类型]
        for i in range(len(self.outputs)):    #写入输出中的验证脚本
            self.outputs[i].script_type = script_types[i]
            self.outputs[i].script = self.output_script_gen(self.outputs[i].script,script_types[i],M,N)
        for i in range(len(self.inputs)):    #写入输入中的验证脚本
            self.inputs[i].scriptSig = self.input_script_gen(private_key,public_key,prev_outs[i].script_type,prev_outs[i].script,i,M,N)

    def verify(self,prev_outs):    #验证签名，需要传入[用到的txio]
        #print(len(self.inputs))
        for i in range(len(self.inputs)):
            backup = self.clear_input_script()    #清除输入脚本
            #self.inputs[i].scriptSig = prev_outs[i].script    #将需要验证的脚本赋值
            result = self.exec(backup[i] + '\t' + prev_outs[i].script)    #拼接执行验证脚本
            self.restore_input_script(backup)    #恢复输入脚本
            if not(result):
                return False    #验证失败
        return True    #验证成功

    def get_size(self):
        ans = 0
        for i in range(len(self.inputs)):
            ans += self.inputs[i].get_size()
        for i in range(len(self.outputs)):
            ans += self.outputs[i].get_size()
        return ans + 84

    def get_fee(self):
        ans = 0
        for i in range(len(self.inputs)):
            ans += ans#self.inputs[i].
        for i in range(len(self.outputs)):
            ans -= self.outputs[i].value
    
class Merkel:    #merkel tree
    class Coinbase(Tx):    #coinbase，继承Tx类
        def __init__(self,private_key,public_key):    #指定矿工的私钥和公钥
            #metadata
            self.hash = zsign.random_hash(256)    #交易hash(id)
            self.ver = 1
            self.vin_sz = 2
            self.vout_sz = 1
            self.lock_time = 0
            self.size = 404
            self.coinbase = str(random.randint(0,10000))    #coinbase中的任意数据
            #input
            self.inputs = []    #交易输入，一笔
            #output
            self.outputs = []    #交易输出，一笔

            self.set_input([('0' * 256, -1)])    #设置输入
            self.set_output([(25, public_key)])    #设置输出，即矿工自身
            self.sign(private_key,public_key,[],['pay-to-public-key-hash'])    #签名

        def sign(self,private_key,public_key,prev_outs,script_types):    #签名，其中输入不需要签名
            for i in range(len(self.outputs)):
                self.outputs[i].script_type = script_types[i]
                self.outputs[i].script = self.output_script_gen(self.outputs[i].script,script_types[i])
            for i in range(len(self.inputs)):
                self.inputs[i].scriptSig = self.input_script_gen(private_key,public_key,'nothing','',i)

        def is_coinbase(self):    #是否是coinbase
            return True

            
    def __init__(self,n,private_key,public_key):   #需传入容量、矿工私钥、公钥
        self.data = [self.Coinbase(private_key,public_key)]    #交易数据
        self.node = []    #hash树
        self.n = n    #容量

    def append(self,tx):    #增加数据
        self.data.append(tx)

    def get_tx(self,n):    #返回第n笔交易
        return self.data[n]

    def is_full(self):    #是否已满
        if len(self.data) >= self.n:
            return True
        return False

    def get_len(self):    #返回当前指针位置
        return len(self.data)

    def get_hash(self):    #返回树根hash
        print(len(self.node[-1]))
        return self.node[-1][-1]

    def get_size(self):
        ans = 0
        for i in range(len(self.data)):
            ans += self.data[i].get_size()
        cnt = len(self.data)
        while cnt > 0:
            ans += 32 * cnt
            cnt = cnt // 2
        return ans
        
    def calc_hash(self):    #更新整棵树的hash值
        self.node = []
        cnt = len(self.data)
        n = len(self.data)
        
        tmp = []
        for i in range(cnt):    #底层
            tmp.append(zsign.sha256(self.data[i].hash))
        self.node.append(tmp)

        while cnt > 1:    #其余层
            tmp = []
            for i in range(0,cnt,2):
                tmp1 = self.node[-1][i]
                if i+1 < len(self.node[-1]):
                    tmp2 = self.node[-1][i+1]
                else:
                    tmp2 = ''
                tmp.append(zsign.sha256(tmp1+tmp2))
            cnt = cnt // 2
            self.node.append(tmp)
        return self.node[-1][0]    #返回树根hash值

class Block:    #单个区块
    def __init__(self,n,private_key,public_key,prev):
        #需传入merkel tree容量、矿工私钥、公钥、前一个区块的hash值
        #self.coinbase = Tx()
        self.tree = Merkel(n,private_key,public_key)    #merkel tree
        self.prev_block_hash = prev    #前一个区块的hash值
        #区块头
        self.mrkl_root = ""    #merkel tree树根hash
        self.difficulty = 1    #挖矿需要几个0
        self.nounce = 0    #挖矿尝试值
        self.hash = ""    #计算出的hash值
        #矿工的私钥和公钥
        self.private_key = private_key
        self.public_key = public_key

    def get_tx(self,n):    #返回树中第n笔交易
        return self.tree.get_tx(n)

    def get_size(self):
        return self.tree.get_size() + 4 + 4 + len(self.hash)

    def is_full(self):    #树是否已满
        return self.tree.is_full()

    def get_len(self):    #树当前数据长度
        return self.tree.get_len()

    def append(self,tx):    #向树中加入数据
        self.tree.append(tx)

    def update(self):    #更新树的hash值
        self.mrkl_root = self.tree.calc_hash()

    def mine(self):    #挖矿并打包
        start = time.time()
        self.update()    #更新更新树的hash值
        while True:    #不断尝试挖矿
            message = self.prev_block_hash + self.mrkl_root + str(self.difficulty) + str(self.nounce)
            self.hash = zsign.sha256(message)
            if True:
                break
            self.nounce += 1
        #print('message:',message)
        #print('hash:',self.hash,'\n')
        return time.time() - start

class Chain:   #区块链
    def __init__(self,n,private_key,public_key):
        self.dat = [Block(n,private_key,public_key,'0' * 64)]    #所有区块，已初始化第一块
        self.n = n    #merkel tree容量
        self.private_key = private_key    #矿工私钥
        self.public_key = public_key    #矿工公钥

    def get_tx(self,pos):    #pos->(区块序号，树中的交易序号)
        return self.dat[pos[0]].get_tx(pos[1])

    def get_pos(self):    #返回当前指针->(区块序号，树中的交易序号)
        return (len(self.dat) - 1, self.dat[-1].get_len())

    def set_key(self,private_key,public_key):
        self.private_key = private_key
        self.public_key = public_key
     
    def append(self,tx):    #增加交易
        if not(self.dat[-1].is_full()):
            self.dat[-1].append(tx)
        if self.dat[-1].is_full():
            self.dat[-1].mine()
            self.dat.append(Block(self.n,self.private_key,self.public_key,self.dat[-1].hash))

class Bitcoin:    #整个bitcoin系统
    def __init__(self,n,input_num):
        self.chain = None    #区块链
        self.tx_list = {}    #交易列表->hash:(Block_id,Tree_id)
        self.n = n
        self.input_num = input_num
        #self.block_id = 0    
        #self.tree_id = 0

        #设置用户密钥
        tmp = zsign.random_key()
        self.user_private_key = tmp[0]
        self.user_public_key = tmp[1]
        self.user_utxo = []    #用户所有的utxo->(hash,n)

        #设置矿工密钥
        tmp = zsign.random_key()
        self.miner_private_key = tmp[0]
        self.miner_public_key = tmp[1]
        self.chain = Chain(self.n,self.miner_private_key,self.miner_public_key)

        #设置监督者密钥
        tmp = zsign.random_key()
        self.regulator_private_key = tmp[0]
        self.regulator_public_key = tmp[1]

        #给用户初始金额
        for i in range(self.n-1):
            tmp = Tx()
            tmp.set_input([])
            #tmp.set_output([(1000,self.user_public_key)])
            #tmp.sign(self.user_private_key,self.user_public_key,[],['pay-to-public-key'] * 2)
            tmp.set_output([(1000,[self.user_public_key,self.miner_public_key])])
            tmp.sign([self.user_private_key,self.miner_private_key],[self.user_public_key,self.miner_public_key],[],['pay-to-script-hash'] * 2,2,2)
            
            #print('t',len(self.get_tx(tmp.get_hash()).outputs))
            self.chain.append(tmp)
            self.tx_list[tmp.get_hash()] = (0,1)
            self.user_utxo.append((tmp.get_hash(),0))

    def get_tx(self,h):   #根据交易hash返回交易
        pos = self.tx_list[h]
        return self.chain.get_tx(pos)

    def get_tx_output(self,pos):   #(hash,n)，返回交易hash为pos[0]的交易的第pos[1]个输出
        return self.get_tx(pos[0]).outputs[pos[1]]

    def get_tx_output_money(self,pos):   #(hash,n)
        return self.get_tx(pos[0]).get_output_money(pos[1])

    def get_tx_output_key(self,pos):   #(hash,n)
        return self.get_tx(pos[0]).get_output_key(pos[1])

    def get_pos(self):    #返回当前指针
        return self.chain.get_pos()

    def get_curr_block_size(self):
        return self.chain.dat[-1].get_size()

    def verify_tx(self,h):    #验证交易hash为h的交易是否有效
        tx = self.get_tx(h)
        prev_outs = []
        for i in range(len(tx.inputs)):
            h = tx.inputs[i].prev_out_hash    #使用的utxo所属的交易的hash
            n = tx.inputs[i].prev_out_n    #返回这些utxo是交易中的第几笔输出
            prev_outs.append(self.get_tx(h).outputs[n])     #根据hash和n找到输出，作为验证函数的输入
        if len(prev_outs) == 0:
            return (True,0)
        start = time.time()
        result = tx.verify(prev_outs)
        return (result,time.time() -  start)

    def verify_all_tx(self):    #验证所有交易
        t = 0
        r = True
        for h in self.tx_list.keys():
            result = self.verify_tx(h)
            if result[0] == False:
                r = False
            t += result[1]
        return (r,t)

    def mine(self):
        return self.chain.dat[-1].mine()

    def generate_tx(self):    #生成新交易
        start = time.time()
        #新建交易，随机选择utxo、金额，并记录交易hash(id)和余额
        tx = Tx()
        in_money = 0
        in_idx = []
        tx_in = []
        in_idx = random.sample(range(len(self.user_utxo)),self.input_num)
        in_idx.sort()
        for i in range(self.input_num):
            tx_in.append(self.user_utxo[in_idx[i]])
            in_money += self.get_tx_output_money(self.user_utxo[in_idx[i]])
        pay = random.random() * 10
            #h = self.user_utxo[idx][0]
        left = in_money - pay

        #设置输入输出，并签名
        #tx_in = [self.user_utxo[idx]]
        #tx_out = [(pay, zsign.random_key()[1]) , (left, self.user_public_key)]
        tx_out = [(pay, zsign.random_key()[1]) , (left, [self.user_public_key,self.miner_public_key])]
        tx.set_input(tx_in)
        tx.set_output(tx_out)
        prev_outs = []
        for i in range(len(tx_in)):
            prev_outs.append(self.get_tx_output(tx_in[i]))
        #tx.sign(self.user_private_key,self.user_public_key,prev_outs,['pay-to-public-key'] * 2)
        tx.sign([self.user_private_key,self.miner_private_key],[self.user_public_key,self.miner_public_key],prev_outs,['pay-to-public-key-hash','pay-to-script-hash'],2,2)

        #更新用户utxo列表、所有交易字典，并在utxo中删除刚刚使用过的输出
        self.tx_list[tx.get_hash()] = self.get_pos()
        self.user_utxo.append((tx.get_hash(),1))
        self.chain.append(tx)
        for i in range(len(in_idx)):
            del self.user_utxo[in_idx[len(in_idx)-1-i]]
        return time.time() - start

class Test:
    def __init__(self):
        self.bitcoin = None
        
    def gen_ver_time(self):
        for i in range(1,21):
            print('Input = ' + str(i))
            t = 0
            self.bitcoin = Bitcoin(2500,i)
            for j in range(100):
                t += self.bitcoin.generate_tx()
            print('Generate time = ' + str(t) + 's')
            result = self.bitcoin.verify_all_tx()
            print('Verify time = ' + str(result[1]) + 's')
            print(result[0])
            print()

    def block_test(self):
        self.bitcoin = Bitcoin(3000,1)
        step = 50
        a = 1500
        b = 2500
        for i in range(a - 1 - step):    #a - 1 - step
            self.bitcoin.generate_tx()
        label = a
        while label <= b:
            print('Tx = ' + str(label))
            for i in range(step):
                self.bitcoin.generate_tx()
            t = self.bitcoin.mine()
            s = self.bitcoin.get_curr_block_size()
            print('Pack time = ' + str(t) + 's')
            print('Block size = ' + str(s) + 'B')
            print()
            label += step
    
def main():
    a = Test()
    a.gen_ver_time()
    a.block_test()
##    a = Bitcoin()
##    for i in range(100):
##        a.generate_tx()
##    a.verify_all_tx()

    
main()
