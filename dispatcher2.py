#import PPIReader
#import FastaGraber
#from subprocess import call
#from subprocess import Popen, PIPE
from os import chdir, getcwd, environ
import os
import datetime
import sys
import RosettaGraber
from multiprocessing import Process
class dispatcher(RosettaGraber.RosettaGraber):
    def __init__(self, interpred_path=None, logpath='./'):
        self.logpath=logpath
        if not interpred_path:
            super(dispatcher, self).__init__()
        else:
            super(dispatcher, self).__init__(interpred_path=interpred_path)
    def msg(self,msg, tag, level='log'):
        f = open('%s/%s.%s' % (self.logpath, os.path.basename(tag), level) , 'a')
        f.write('#'*10 + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")\
        + '#'*10 + '\n')
        f.write(msg+'\n')
        f.close()
    def progress(self, p):
        print 'Progress: %s/%s' %(p, len(self.scripts))
    def run(self, cpu=32):
        def handler(s):
            output, err = RosettaGraber.RosettaGraber.caller(s)
            self.msg(msg=output, tag=s)
            self.msg(msg=err, tag=s, level='err')
        for i in xrange(0,len(self.scripts), cpu):
            self.progress(i*cpu)
            plist = []
            for s in self.scripts[i:i+cpu]:
                print s
                proc = Process(target=handler,
                    args=(s,)
                )
                proc.start()
                plist.append(proc)
            for p in plist:
                p.join()
        print 'done'
    def test(self):
        def handler(s):
            output, err = RosettaGraber.RosettaGraber.caller(s)
            self.msg(msg=output, tag=s)
            self.msg(msg=err, tag=s, level='err')
        plist = []
        for s in self.scripts[:10]:
            print s
            proc = Process(target=handler,
                args=(s,)
            )
            proc.start()
            plist.append(proc)
        for p in plist:
            p.join()
        print 'done'
            
    def singletest(self):
        my_env = environ.copy()
        print RosettaGraber.RosettaGraber.caller(self.scripts[0])
        print 'done'
        
if __name__ == '__main__':
    dp = dispatcher(
        interpred_path=sys.argv[1],
        logpath=sys.argv[2]
    )
    dp.run()
