import socket
import sys
import dns
import pprint
import cStringIO
import pdb

DNS = ("8.8.8.8", 53) 

CATS = (
    "4.36.66.178",
    "8.7.198.45",
    "37.61.54.158",
    "46.82.174.68",
    "59.24.3.173",
    "64.33.88.161",
    "64.33.99.47",
    "64.66.163.251",
    "65.104.202.252",
    "65.160.219.113",
    "66.45.252.237",
    "72.14.205.99",
    "72.14.205.104",
    "78.16.49.15",
    "93.46.8.89",
    "128.121.126.139",
    "159.106.121.75",
    "169.132.13.103",
    "192.67.198.6",
    "202.106.1.2",
    "202.181.7.85",
    "203.98.7.65",
    "203.161.230.171",
    "207.12.88.98",
    "208.56.31.43",
    "209.36.73.33",
    "209.145.54.50",
    "209.220.30.174",
    "211.94.66.147",
    "213.169.251.35",
    "216.221.188.182",
    "216.234.179.13",
    "243.185.187.39",
    )



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
