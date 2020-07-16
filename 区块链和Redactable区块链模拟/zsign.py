#-*- coding:utf-8 -*-
from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Hash import SHA256
from Crypto.Hash import RIPEMD160
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
import base64
import random

class Tx:
    class Input:
        def __init__(self):
            self.prev_out_hash = ""
            self.prev_out_n = 0
            self.scriptSig = ""
            self.user = -1
   
    class Output:
        def __init__ (self):
            self.value = 0
            self.scriptPubKey = ""
            self.user = -1
            
    def __init__(self):
        #metadata
        self.hash = ""
        self.ver = 1
        self.vin_sz = 2
        self.vout_sz = 1
        self.lock_time = 0
        self.size = 404
        #input
        self.inputs = [self.Input()]
        #output
        self.outputs = []    

def random_key():
    # 伪随机数生成器
    random_generator = Random.new().read
    # rsa算法生成实例
    rsa = RSA.generate(1024, random_generator)
    # A的秘钥对的生成
    private_pem = rsa.exportKey()
    public_pem = rsa.publickey().exportKey()
    return (private_pem, public_pem)

def verify(message,signature,public_key):
    rsakey = RSA.importKey(public_key)
    verifier = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA.new()
    digest.update(str(message).encode("utf8"))
    is_verify = verifier.verify(digest, base64.b64decode(signature))
    return is_verify

def sign(message,private_key):
    rsakey = RSA.importKey(private_key)
    signer = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA.new()
    digest.update(message.encode("utf8"))
    sign = signer.sign(digest)
    signature = base64.b64encode(sign)
    return signature

def hash160(message):
    sha = SHA256.new()
    sha.update(message.encode('utf-8'))
    x = sha.hexdigest()
    ripemd = RIPEMD160.new()
    ripemd.update(x.encode('utf-8'))
    y = ripemd.hexdigest()
    return y

def sha256(message):
    sha = SHA256.new()
    sha.update(message.encode('utf-8'))
    x = sha.hexdigest()
    return x

def to_dict(obj,cover = []):
    if not(hasattr(obj,'__dict__')):
        return {'dat':obj}
    original = vars(obj).items()
    ans = {}
    for i,j in original:
        if hasattr(j,'__dict__'):
            ans[i] = to_str(j,cover)
        elif isinstance(j,list) or isinstance(j,tuple):
            tmp = []
            for k in j:
                tmp.append(to_dict(k,cover))
            ans[i] = tmp
        elif i not in cover:
            ans[i] = j
    return ans

def to_str(obj,cover = []):
    return str(to_dict(obj,cover))

def random_hash(n):
    dat = '0123456789abcdef'
    ans = ''
    for i in range(n):
        ans = ans + dat[random.randint(0,15)]
    return ans

def main():
    message = "Touhou Project"
    keys = random_key()
    z = sign(message,keys[0])
    print(z,type(z))
    verify(message,z,keys[1])
    print(hash160(message))
#main()

