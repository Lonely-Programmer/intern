from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64
import json
import random
import zsign
import time

class Tx:
    class Input:
        def __init__(self):
            self.prev_out_hash = ""
            self.prev_out_n = -1
            self.scriptSig = ""
            #self.script_type = ""
            self.public_key = ""

        def set_data(self,dat):   #(prev_out_hash,prev_out_n)
            self.prev_out_hash = dat[0]
            self.prev_out_n = dat[1]
   
    class Output:
        def __init__ (self):
            self.value = 0
            #self.scriptPubKey = ""
            self.script = ""
            self.script_type = ""

        def set_data(self,dat):   #(value,public_key)
            self.value = dat[0]
            self.script = dat[1]
            
    def __init__(self):
        #metadata
        self.hash = zsign.random_hash(256)
        self.ver = 1
        self.vin_sz = 2
        self.vout_sz = 1
        self.lock_time = 0
        self.size = 404
        #input
        self.inputs = []
        #output
        self.outputs = []

    def is_coinbase(self):
        return False

    def get_hash(self):
        return self.hash

    def get_input_data(self,n):
        tmp = self.inputs[n]
        return (tmp.prev_out_hash,tmp.prev_out_n,tmp.scriptSig,tmp.public_key)

    def get_output_money(self,n):
        return self.outputs[n].value

    def get_output_key(self,n):
        return self.outputs[n].public_key

    def set_input(self,dat):   #[(prev_out_hash,prev_out_n),...]
        self.inputs = []
        for i in range(len(dat)):
            self.inputs.append(self.Input())
            self.inputs[i].set_data(dat[i])

    def set_output(self,dat):   #[(value,public_key),...]
        self.outputs = []
        for i in range(len(dat)):
            self.outputs.append(self.Output())
            self.outputs[i].set_data(dat[i])

    def checksig(self,sig,public_key):
        return zsign.verify(self.calc_hash(),sig,public_key)

    def exec(self,script):
        op = script.split('\t')
        stack = []
        
        for i in range(len(op)):
##            print(stack)
##            print(op[i])
##            print()
            if op[i] == 'OP_DUP':
                stack.append(stack[-1])
            elif op[i] == 'OP_HASH160':
                #print(type(stack[-1]))
                stack[-1] = zsign.hash160(stack[-1])
                #print('e:',stack[-1],'\n',stack[-2])
            elif op[i] == 'OP_EQUALVERIFY':
                #print('e:',stack[-1],'\n',stack[-2])
                if stack[-1] != stack[-2]:
                    print('EQU!\n')
                    return False
                del stack[-1]
                del stack[-1]
            elif op[i] == 'OP_CHECKSIG':
                if not(self.checksig(bytes(stack[-2], encoding = 'utf-8'),bytes(stack[-1], encoding = 'utf-8'))):
                    print('SIG!\n')
                    return False
                del stack[-1]
                del stack[-1]
            else:
                stack.append(op[i])
        if len(stack) > 0:
            return False
        return True

    def clear_input_script(self):
        backup = []
        for i in range(len(self.inputs)):
            backup.append(self.inputs[i].scriptSig)
            self.inputs[i].scriptSig = ''
        return backup

    def restore_input_script(self,backup):
        for i in range(len(self.inputs)):
            self.inputs[i].scriptSig = backup[i]

    def calc_hash(self):
        #print('sha:',zsign.sha(zsign.to_str(self)))
        #print('to_str:',zsign.to_str(self),'\n')
        
        return zsign.hash160(zsign.to_str(self))

    def output_script_gen(self,output_public_key,script_type):
        if script_type == 'pay-to-script-hash':
            tmp = zsign.hash160(str(output_public_key,encoding='utf-8'))
            #print('sign key:',output_public_key,'\n',tmp,'\n')
            ans = 'OP_DUP\tOP_HASH160\t' + tmp + '\tOP_EQUALVERIFY\tOP_CHECKSIG'

        return ans

    def input_script_gen(self,private_key,public_key,script_type,output_script,input_idx):
        if script_type == 'nothing':
            return 'nothing'
        if script_type == 'pay-to-script-hash':
            backup = self.clear_input_script()
            self.inputs[input_idx].scriptSig = output_script
            sig = zsign.sign(self.calc_hash(),private_key)
            self.restore_input_script(backup)
            return str(sig, encoding='utf-8') + '\t' + str(public_key, encoding='utf-8')

    def sign(self,private_key,public_key,prev_outs,script_types):
        for i in range(len(self.outputs)):
            self.outputs[i].script_type = script_types[i]
            self.outputs[i].script = self.output_script_gen(self.outputs[i].script,script_types[i])
        for i in range(len(self.inputs)):
            self.inputs[i].scriptSig = self.input_script_gen(private_key,public_key,prev_outs[i].script_type,prev_outs[i].script,i)

    def verify(self,prev_outs):
        print(len(self.inputs))
        for i in range(len(self.inputs)):
            backup = self.clear_input_script()
            self.inputs[i].scriptSig = prev_outs[i].script
            result = self.exec(backup[i] + '\t' + prev_outs[i].script)
            self.restore_input_script(backup)
            if not(result):
                return False
        return True

    def get_fee(self):
        ans = 0
        for i in range(len(self.inputs)):
            ans += ans#self.inputs[i].
        for i in range(len(self.outputs)):
            ans -= self.outputs[i].value
    
class Merkel:
    class Coinbase(Tx):
        def __init__(self,private_key,public_key):
            #metadata
            self.hash = zsign.random_hash(256)
            self.ver = 1
            self.vin_sz = 2
            self.vout_sz = 1
            self.lock_time = 0
            self.size = 404
            self.coinbase = str(random.randint(0,10000))
            #input
            self.inputs = []
            #output
            self.outputs = []

            self.set_input([('0' * 256, -1)])
            self.set_output([(25, public_key)])
            self.sign(private_key,public_key,[],['pay-to-script-hash'])

        def sign(self,private_key,public_key,prev_outs,script_types):
            for i in range(len(self.outputs)):
                self.outputs[i].script_type = script_types[i]
                self.outputs[i].script = self.output_script_gen(self.outputs[i].script,script_types[i])
            for i in range(len(self.inputs)):
                self.inputs[i].scriptSig = self.input_script_gen(private_key,public_key,'nothing','',i)

            
    def __init__(self,n,private_key,public_key):
        self.data = [self.Coinbase(private_key,public_key)]
        self.node = []
        self.n = n

    def append(self,tx):
        self.data.append(tx)

    def get_tx(self,n):
        return self.data[n]

    def is_full(self):
        if len(self.data) >= self.n:
            return True
        return False

    def get_len(self):
        return len(self.data)

    def get_hash(self):
        print(len(self.node[-1]))
        return self.node[-1][-1]
        
    def calc_hash(self):
        self.node = []
        cnt = len(self.data)
        n = len(self.data)
        
        tmp = []
        for i in range(cnt):
            tmp.append(zsign.sha256(self.data[i].hash))
        self.node.append(tmp)

        while cnt > 1:
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
        return self.node[-1][0]

class Block:
    def __init__(self,n,private_key,public_key,prev):
        self.coinbase = Tx()
        self.tree = Merkel(n,private_key,public_key)
        self.prev_block_hash = prev
        self.mrkl_root = ""
        self.difficulty = 1
        self.nounce = 0
        self.hash = ""
        self.private_key = private_key
        self.public_key = public_key

    def get_tx(self,n):
        return self.tree.get_tx(n)

    def is_full(self):
        return self.tree.is_full()

    def get_len(self):
        return self.tree.get_len()

    def append(self,tx):
        self.tree.append(tx)

    def update(self):
        self.mrkl_root = self.tree.calc_hash()

    def mine(self):
        self.update()
        while True:
            message = self.prev_block_hash + self.mrkl_root + str(self.difficulty) + str(self.nounce)
            value = '0' * self.difficulty + 'f' * (256 - self.difficulty)
            self.hash = zsign.sha256(message)
            if self.hash < value:
                break
            self.nounce += 1
        print('message:',message)
        print('hash:',self.hash,'\n')

class Chain:
    def __init__(self,n,private_key,public_key):
        self.dat = [Block(n,private_key,public_key,'0' * 64)]
        self.n = n
        self.private_key = private_key
        self.public_key = public_key

    def get_tx(self,pos):
        return self.dat[pos[0]].get_tx(pos[1])

    def get_pos(self):
        return (len(self.dat) - 1, self.dat[-1].get_len())

    def set_key(self,private_key,public_key):
        self.private_key = private_key
        self.public_key = public_key
     
    def append(self,tx):
        if not(self.dat[-1].is_full()):
            self.dat[-1].append(tx)
        if self.dat[-1].is_full():
            self.dat[-1].mine()
            self.dat.append(Block(self.n,self.private_key,self.public_key,self.dat[-1].hash))

class Bitcoin: 
    def __init__(self):
        self.chain = None
        self.tx_list = {}   #hash:(Block_id,Tree_id)
        self.block_id = 0
        self.tree_id = 0

        tmp = zsign.random_key()
        self.user_private_key = tmp[0]
        self.user_public_key = tmp[1]
        self.user_utxo = []   #(hash,n)
        
        tmp = zsign.random_key()
        self.miner_private_key = tmp[0]
        self.miner_public_key = tmp[1]
        self.chain = Chain(16,self.miner_private_key,self.miner_public_key)
        
        tmp = zsign.random_key()
        self.supervisor_private_key = tmp[0]
        self.supervisor_public_key = tmp[1]
        
        tmp = Tx()
        tmp.set_input([])
        tmp.set_output([(1000,self.user_public_key)])
        tmp.sign(self.user_private_key,self.user_public_key,[],['pay-to-script-hash'] * 2)
        #print('t',len(self.get_tx(tmp.get_hash()).outputs))
        self.chain.append(tmp)
        self.tx_list[tmp.get_hash()] = (0,1)
        self.user_utxo.append((tmp.get_hash(),0))

    def is_coinbase(self):
        return True

    def get_tx(self,h):   #hash
        pos = self.tx_list[h]
        return self.chain.get_tx(pos)

    def get_tx_output(self,pos):   #(hash,n)
        return self.get_tx(pos[0]).outputs[pos[1]]

    def get_tx_output_money(self,pos):   #(hash,n)
        return self.get_tx(pos[0]).get_output_money(pos[1])

    def get_tx_output_key(self,pos):   #(hash,n)
        return self.get_tx(pos[0]).get_output_key(pos[1])

    def get_pos(self):
        return self.chain.get_pos()

    def verify_tx(self,h):
        tx = self.get_tx(h)
        prev_outs = []
        for i in range(len(tx.inputs)):
            h = tx.inputs[i].prev_out_hash
            n = tx.inputs[i].prev_out_n
            prev_outs.append(self.get_tx(h).outputs[n])
        return tx.verify(prev_outs)

    def verify_all_tx(self):
        for h in self.tx_list.keys():
            print(self.verify_tx(h))

    def generate_tx(self):
        tx = Tx()
        idx = random.randint(0,len(self.user_utxo)-1)
        pay = random.random() * 10
        h = self.user_utxo[idx][0]
        left = self.get_tx_output_money(self.user_utxo[idx]) - pay
        
        tx_in = [self.user_utxo[idx]]
        tx_out = [(pay, zsign.random_key()[1]) , (left, self.user_public_key)]
        tx.set_input(tx_in)
        tx.set_output(tx_out)
        prev_outs = []
        for i in range(len(tx_in)):
            prev_outs.append(self.get_tx_output(tx_in[i]))
        tx.sign(self.user_private_key,self.user_public_key,prev_outs,['pay-to-script-hash'] * 2)

        self.tx_list[tx.get_hash()] = self.get_pos()
        self.user_utxo.append((tx.get_hash(),1))
        self.chain.append(tx)
        del self.user_utxo[idx]

    def mine(self):
        pass
    
    
def main():
    a = Bitcoin()
    for i in range(100):
        a.generate_tx()
    a.verify_all_tx()

start = time.time()
main()
print("time:",time.time() - start)
