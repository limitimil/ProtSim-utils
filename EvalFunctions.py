#this script was finished under /home/limin/project
#this file has been copied to /home/limin/limin/InterPred on 2017-12-20
import os
import re
def evaluation(path):
    read = open(path).read()
    table = re.split('##+',read)[-1].strip().split('\n')
    header,body = table[0], table[1:]
    body = map(lambda x: 
        map( lambda y:
        y.strip(),
        x.split('|')[:2]
        ), 
        body
    )
    return sorted(body, key=lambda x: float(x[1]))

if __name__ == '__main__':
    import sys
    print evaluation(sys.argv[1])
