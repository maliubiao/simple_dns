#! /usr/bin/env python
import socket
import select
import gfw
import dns
import struct
import time
import pdb
import signal
import cStringIO
import os
import sys
import pwd

g = globals() 

DNS_SERVER = ("8.8.8.8", 53)

SERVER = ("", 53)

LOG = "/tmp/localdns.log"
PID = "/tmp/localdns.pid" 
USER = "nobody"

#10s
REQUEST_TIMEOUT = 10

#ident -> client
itable = {} 

has_epoll = False


if hasattr(select, "epoll"):
    has_epoll = True 


def set_globals(): 
    g["myloc"] = os.path.join(os.getcwd(), __file__)
    g["sock"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    g["sockfd"] = sock.fileno()
    sock.bind(SERVER) 
    sock.settimeout(0)
    if has_epoll:
        g["p"] = select.epoll()
        p.register(sockfd, select.EPOLLIN |select.EPOLLERR) 


def cat_test(packet):
    found = True 
    for i in packet["answer"]:
        if not "addr" in i:
            return False
        if i["addr"] in gfw.CATS:
            found = False 
    if not found:
        return True 
    else:
        return False


def handle_pollin(): 
    data, client = sock.recvfrom(4096) 
    if len(data) < 12:
        #not a dns packet
        return
    b = cStringIO.StringIO(data) 
    unknown = False 
    try:
        ret = dns.parse_stream(b)
    except ValueError:
        unknown = True 
        print "parse error, ignore" 
    finally:
        b.close() 
    if unknown:
        ident = struct.unpack(">H", data[:2])[0] 
    else:
        ident = ret["ident"] 
        if cat_test(ret): 
            print "GFW: you shall not pass"
            return
    if client == DNS_SERVER: 
        #forward to CLIENT 
        if not ident in itable:
            return 
        client = itable[ident][0] 
        sock.sendto(data, client) 
        del itable[ident]
    else: 
        if not unknown:
            for k in ret["question"]: 
                if "name" in k:
                    print "query name: ", k["name"], "from: %s" % (client[0])
        itable[ident]  = (client, time.time())
        sock.sendto(data, DNS_SERVER) 


def wait_request_epoll(timeout): 
    for fd, event in p.poll(timeout): 
        if event & select.EPOLLIN: 
            try:
                handle_pollin()
            except IOError:
                pass
        if event & select.EPOLLERR:
            raise Exception("Failed") 

def wait_request_select(timeout):
    r, _, e = select.select([sockfd], [], [sockfd], timeout)    
    if sockfd in r:
        try:
            handle_pollin()
        except IOError:
            pass
    if sockfd in e:
        raise Exception("Failed")


def bgrun():
    log_file = open(LOG, "w+", buffering=False)
    pid_file = open(PID, "w+", buffering=False)
    try:
        status = os.fork()
    except OSError as e:
        print e
    if not status:
        os.setsid() 
        sys.stdin = open("/dev/null", "r")
        sys.stdout = log_file
        sys.stderr = log_file 
        try:
            status2 = os.fork()
        except OSError as e:
            print e
        if status2: 
            pid_file.write(str(status2))
            pid_file.close()
            exit() 

    else:
        exit() 

def run_as_user(user):
    try:
        db = pwd.getpwnam(user)
    except KeyError:
        raise Exception("user doesn't exists") 
    try:
        os.setgid(db.pw_gid)
    except OSError:        
        raise Exception("change gid failed") 
    try:
        os.setuid(db.pw_uid)
    except OSError:
        raise Exception("change uid failed") 

def clients_gc():
    now = time.time()
    for k, v in itable.items(): 
        if now - v[1] > 2:
            del itable[k] 


def sigusr1_reload(*args):
    print "reload localdns"
    os.execvp("python", ["python", myloc]) 


def main():
    signal.signal(signal.SIGUSR1, sigusr1_reload)
    wait_request = wait_request_select
    if has_epoll:
        wait_request = wait_request_epoll 
    set_globals() 
    bgrun() 
    run_as_user(USER) 
    end = 0
    prev = time.time()
    while True: 
        end = time.time()
        try:
            wait_request(2)
        except IOError:
            pass
        if end - prev > REQUEST_TIMEOUT: 
            clients_gc()
            prev = time.time()

if __name__ == "__main__":
    main() 

