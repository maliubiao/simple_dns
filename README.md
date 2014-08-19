#dns tools

##sample output 
###localdns.py
```shell 
$ python localdns.py 
query name:  dropbox.com
query name:  dropbox.com
GFW: you shall not pass
query name:  dropbox.com
GFW: you shall not pass
query name:  dropbox.com
query name:  dropbox.com
GFW: you shall not pass
query name:  dropbox.com
GFW: you shall not pass
query name:  mail.google.com
query name:  mail.google.com
query name:  mail.google.com
query name:  dropbox.com
GFW: you shall not pass
query name:  dropbox.com
GFW: you shall not pass
query name:  web.pinyin.sogou.com
...
```
###gfw.py
```shell
$ python gfw.py youtube.com
{'additional': [],
 'answer': [{'addr': '173.194.127.35',
             'cls': 1,
             'name': 'youtube.com',
             'ttl': 299,
             'type': 1},
            {'addr': '173.194.127.33',
             'cls': 1,
             'name': 'youtube.com',
             'ttl': 299,
             'type': 1},
            {'addr': '173.194.127.40',
             'cls': 1,
             'name': 'youtube.com',
             'ttl': 299,
             'type': 1},
            {'addr': '173.194.127.38',
             'cls': 1,
             'name': 'youtube.com',
             'ttl': 299,
             'type': 1},
            {'addr': '173.194.127.32',
             'cls': 1,
             'name': 'youtube.com',
             'ttl': 299,
             'type': 1},
            {'addr': '173.194.127.39',
             'cls': 1,
             'name': 'youtube.com',
             'ttl': 299,
             'type': 1},
            {'addr': '173.194.127.46',
             'cls': 1,
             'name': 'youtube.com',
             'ttl': 299,
             'type': 1},
            {'addr': '173.194.127.34',                                                                 
             'cls': 1,                                                                                 
             'name': 'youtube.com',                                                                    
             'ttl': 299,                                                                               
             'type': 1},                                                                               
            {'addr': '173.194.127.36',                                                                 
             'cls': 1,
             'name': 'youtube.com',
             'ttl': 299,
             'type': 1},
            {'addr': '173.194.127.37',
             'cls': 1,
             'name': 'youtube.com',
             'ttl': 299,
             'type': 1},
            {'addr': '173.194.127.41',
             'cls': 1,
             'name': 'youtube.com',
             'ttl': 299,
             'type': 1}],
 'authority': [],
 'flags': 33152,
 'ident': 52580,
 'question': [{'cls': 1, 'name': 'youtube.com', 'type': 1}]}
```

