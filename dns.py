#-*-encoding=utf-8-*-
import socket
import os 
import struct 
import io 
import pdb 
import cStringIO


#Address Resource Record
TYPE_ADDR = 1
#Name Server Resource Record
TYPE_NS = 2
#Mail Destination, Obsolete
TYPE_MD = 3
#Mail Forwarder, Obsolete
TYPE_MF = 4 
#Canonical Name Resource Record
TYPE_CNAME = 5
#Start Of Authority Resource Record
TYPE_SOA = 6
#Mailbox Domain Name
TYPE_MB = 7
#Mail Group member
TYPE_MG = 8
#Mail Rename Domain Name
TYPE_MR = 9
#NULL RR
TYPE_NULL = 10
#Well Known Service Description
TYPE_WKS = 11 
#Domain Name Pointer
TYPE_PTR = 12
#Host Information
TYPE_HINFO = 13
#MailBox or Mail List Information
TYPE_MINFO = 14 
#Mail Exchange Resource Record
TYPE_MX = 15
#Text Resource Record
TYPE_TR = 16 
#IPV6 Addr
TYPE_AAAA = 28 
TYPE_SRV  = 33
#OPT 
TYPE_OPT = 41

#question type only
#Transfer of an Entire Zone
TYPE_AXFR = 252
#MailBox-related RRs
TYPE_MAILB = 253
#Mail Agent RRs
TYPE_MAILA = 254
#All record
TYPE_ALL = 255

#question class
CLASS_INET = 1
CLASS_CSNET = 2
CLASS_CHAOS = 3
CLASS_HESIOD = 4
CLASS_ANY = 255

rcode = {
        1: "No Error",
        2: "FormatError",
        3: "Server Failure",
        4: "Name Error",
        5: "Refused",
        6: "YX Domain",
        7: "YX RR Set",
        8: "NX RR Set",
        9: "No Auth",
        10: "No Zone"
        } 

QR = 1 << 15
AA = 1 << 10
TC = 1 << 9
RD = 1 << 8
RA = 1 << 7

NEED_MORE = 0x2014816

def compress_test(byte):
    if 0b11000000 & ord(byte):
        return True        
    else:
        return False


def convert_host(host):
    b = []
    for i in host.split("."):
        b.append(chr(len(i)))
        b.append(i)
    b.append("\x00")
    return "".join(b)


def query_header(flag): 
    msg = []
    msg.append(os.urandom(2)) #ident 
    flag |= 0b0000000000000000 #query 
    flag |= 0b0000000000000000 #opcode query 
    flag |= 0b0000000000000000 #authoritative answer flag
    flag |= 0b0000000000000000 #truncated false
    flag |= RD #recursion desired true
    flag |= 0b0000000000000000 #zbit
    flag |= 0b0000000000100000 #AD bit
    flag |= 0b0000000000000000 #Non-ahtenticated data: Unacceptable
    msg.append(struct.pack(">H", flag))
    return "".join(msg)


def question_addr(host):
    msg = []
    msg.append(convert_host(host))
    msg.append(struct.pack(">H", TYPE_ADDR)) #host address
    msg.append(struct.pack(">H", CLASS_INET)) #internet
    return "".join(msg)

def question_ns(host):
    msg = []
    msg.append(convert_host(host))
    msg.append(struct.pack(">H", TYPE_NS)) #name server
    msg.append(struct.pack(">H", CLASS_INET)) #internet
    return "".join(msg) 

#not avaiable
def batch_query(hlist): 
    msg = []
    msg.append(query_header(0))
    msg.append(struct.pack(">H", len(hlist)))
    msg.append(struct.pack(">H", 0))
    msg.append(struct.pack(">H", 0))
    msg.append(struct.pack(">H", 0))
    for i in hlist:
        msg.append(question_addr(i))
    return "".join(msg)    


def query_addr(host):
    msg = []
    msg.append(query_header(0))
    #nums
    msg.append(struct.pack(">H", 1)) #one query
    msg.append(struct.pack(">H", 0)) 
    msg.append(struct.pack(">H", 0))
    msg.append(struct.pack(">H", 0))
    #one query
    msg.append(question_addr(host))
    return "".join(msg)


def query_ns(host):
    msg = []
    msg.append(query_header(0))
    #nums
    msg.append(struct.pack(">H", 1)) #one query
    msg.append(struct.pack(">H", 0)) 
    msg.append(struct.pack(">H", 0))
    msg.append(struct.pack(">H", 0))
    #one query
    msg.append(question_ns(host))
    return "".join(msg)


def handle_goto(b):
    b.seek(-1, io.SEEK_CUR) 
    d = b.read(2)
    if len(d) < 2:
        raise ValueError(NEED_MORE)
    twobyte = struct.unpack(">H", d)[0]
    #before goto
    prev = b.tell()
    where = twobyte & 0b111111 
    b.seek(where, io.SEEK_SET)
    return prev 


def parse_name(b): 
    stack = [] 
    nb = [] 
    mz = 0
    mx = 36
    while True: 
        while True: 
            mz += 1
            if mz > mx:
                raise ValueError("parse name error")
            byte = b.read(1) 
            if not byte:
                break
            if compress_test(byte): 
                prev = handle_goto(b) 
                nexto = b.tell() 
                #loop ends
                found = False
                for i, v in enumerate(stack): 
                    if nexto >= min(v) and nexto <= max(v):
                        b.seek(v[0], io.SEEK_SET)
                        del stack[i:]
                        found = True
                        break
                if found:
                    break
                stack.append((prev, nexto)) 
                continue 
            count = ord(byte)  
            if not count:
                if stack: 
                    prev, _ = stack.pop() 
                    b.seek(prev, io.SEEK_SET) 
                break
            d = b.read(count)
            if len(d) < count:
                raise ValueError(NEED_MORE)
            nb.append(d) 
        mz += 1
        #avoid infinite goto
        if mz > mx:
            raise ValueError("parse name error")
        #done
        if not stack:
            break 
    return ".".join(nb)


def parse_question(b):
    a = {}
    a["name"] = parse_name(b)
    d = b.read(4)
    if len(d) < 4:
        raise ValueError(NEED_MORE)
    a["type"], a["cls"] = struct.unpack(">HH", d) 
    return a 


def parse_record(b, flag): 
    a = {} 
    a["name"] = parse_name(b) 
    d = b.read(10)
    if len(d) < 10:
        raise ValueError(NEED_MORE)
    tp, cls, ttl, rl = struct.unpack(">HHIH", d) 
    a["type"] = tp
    a["ttl"] = ttl
    a["cls"] = cls 
    if tp == TYPE_ADDR:        
        a["addr"] = socket.inet_ntoa(b.read(rl)) 
    elif tp == TYPE_NS:            
        a["name"] = parse_name(b) 
    elif tp == TYPE_CNAME:
        a["name"] = parse_name(b) 
    elif tp == TYPE_SOA: 
        a["master"] = parse_name(b)
        a["responsible"] = parse_name(b)
        if not flag & 0xf:
            d = b.read(20)
            if len(d) == 20:
                a["serial"], a["refresh"], a["retry"], a["expire"], a["minimum"] = struct.unpack(">IIIII", d) 
    elif tp == TYPE_PTR:
        a["ptr"] = parse_name(b) 
    elif tp == TYPE_MX: 
        d = b.read(2)
        if len(d) < 2:
            raise ValueError(NEED_MORE)
        a["preference"] = struct.unpack(">H", d)[0]
        a["exchange"] = parse_name(b) 
    elif tp == TYPE_TR:
        a["text"] = b.read(rl)
    elif tp == TYPE_AAAA:
        a["addr"] = socket.inet_ntop(socket.AF_INET6, b.read(rl))
    elif tp == TYPE_OPT: 
        a["payload"] = cls
        del a["cls"] 
        a["option"] = ttl
        del a["ttl"] 
    return a



def parse_stream(b): 
    d = b.read(12)
    if len(d) < 12:
        raise ValueError(NEED_MORE)
    ident, flag, qn, ann, arn, adn = struct.unpack(">HHHHHH", d) 
    ret = {
            "ident": ident,
            "flags": flag,
            "question": [],
            "answer": [],
            "authority": [],
            "additional": []
            } 
    for i in range(qn):
        ret["question"].append(parse_question(b)) 
    for k, v in zip(("answer", "authority", "additional"),
            (ann, arn, adn)):
        for i in range(v): 
            ret[k].append(parse_record(b, flag))
    b.close()
    return ret 
