import socket
import sys
import dns
import pprint
import cStringIO
import pdb

DNS = ("8.8.8.8", 53) 

CATS = { 
    "1.1.1.1": None, 
    "4.36.66.178": None,
    "8.7.198.45": None,
    "23.89.5.60": None, 
    "37.61.54.158": None,
    "37.208.111.120":None,
    "46.82.174.68": None,
    "49.2.123.56": None,
    "54.76.135.1": None,
    "59.24.3.173": None,
    "64.33.88.161": None,
    "64.33.99.47": None,
    "64.66.163.251": None,
    "65.104.202.252": None,
    "65.160.219.113": None,
    "66.45.252.237": None,
    "72.14.205.99": None,
    "72.14.205.104": None, 
    "74.125.127.102": None,
    "74.125.155.102": None,
    "74.125.39.102": None,
    "74.125.39.113": None,
    "77.4.7.92": None,
    "78.16.49.15": None,
    "93.46.8.89": None,
    "128.121.126.139": None,
    "159.106.121.75": None,
    "169.132.13.103": None,
    "118.5.49.6": None,
    "188.5.4.96": None,
    "189.163.17.5": None,
    "192.67.198.6": None,
    "197.4.4.12": None,
    "202.106.1.2": None,
    "202.181.7.85": None,
    "203.98.7.65": None,
    "203.161.230.171": None,
    "207.12.88.98": None,
    "208.56.31.43": None,
    "209.36.73.33": None,
    "209.85.229.138": None,
    "209.145.54.50": None,
    "209.220.30.174": None,
    "211.94.66.147": None,
    "213.169.251.35": None,
    "216.221.188.182": None,
    "216.234.179.13": None, 
    "243.185.187.3": None,
    "243.185.187.39": None,
    "249.129.46.48": None,
    "253.157.14.165": None,
    "255.255.255.255": None, 
    } 

if __name__ == "__main__": 
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

    def send_query(msg): 
        s.sendto(msg, DNS)

    def recv_query():
        #only msg
        return s.recvfrom(4096)[0] 
    #send request
    send_query(dns.query_addr(sys.argv[1])) 
    while True: 
        msg =  recv_query() 
        b = cStringIO.StringIO(msg)
        ret = dns.parse_stream(b) 
        b.close()
        found = True
        for i in ret["answer"]:
            if i["addr"] in CATS:
                found = False
        if found:
            break 
    pprint.pprint(ret)
