import os
import signal
import PPIReader
import FastaGraber
from subprocess import call
from subprocess import Popen, PIPE
from os import chdir, getcwd, environ
import datetime
class dispatcher(PPIReader.PPIReader):
    interpred_use_python = "/home/limin/bin/modeller9.15/bin/modpy.sh python2.7"
    interpred_executable = 'InterPred.py'
    context='./'
    cpu=None
    def setFastaGraber(self,repo='./flattened',
    mapping='./uniprot_mapping.csv'):
        self.FG = FastaGraber.FastaGraber(repo=repo,mapping=mapping)
        return
    def arrangeCall(self,fas1,fas2,cpu=32):
        if self.cpu:
            cpu =self.cpu
        return [self.interpred_use_python, 
            self.interpred_executable,
            '-fasta',
            self.context + '/' + fas1,
            self.context + '/' + fas2,
            '-cpu',
            str(cpu)
        ]
    def log(self,msg, filename='./log', stdout=False):
        f = open(self.context + '/' + filename, 'a')
        f.write('#'*10 + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + '#'*10 + '\n')
        f.write(msg + '\n')
        f.close()
        if stdout:
           print msg 
    def errlog(self,msg ,filename='./errlog', stdout=False):
        f = open(self.context + '/' + filename, 'a')
        f.write('#'*10 + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + '#'*10 + '\n')
        f.write(msg + '\n')
        f.close()
        if stdout:
           print msg 
    def run(self, skipList=[]):
        def done(p1,p2):
            p1 = p1.split('/')[2].split('.')[0]
            p2 = p2.split('/')[2].split('.')[0]
            for i in skipList:
                if i[0] == p1 and i[1] == p2:
                    print 'done %s, %s'% (p1,p2)
                    raise Exception('modeling for %s and %s has done' %(p1,p2))
            return None 
        self.setFastaGraber()
        #in test session we just try PPI for FGFR3
        self.context=getcwd()
        my_env = environ.copy()
        for mp in self.ppi.keys(): #membrane proteins
            try:
                fas1 = self.FG.grabPathByGene(mp)
            except Exception as e:
                self.errlog(str(e), stdout=True)
                self.errlog('skip modeling %s v.s. *' % mp, stdout=True)
                continue
                
                
            for p in self.ppi[mp]: 
                print 'working on %s v.s. %s' % (mp, p)
                try:
                    fas2 = self.FG.grabPathByGene(p)
                    done(fas1,fas2)
                    chdir('/home/limin/limin/InterPred/interpred/')
                    proc= Popen(' '.join( self.arrangeCall(
                        fas1= fas1,
                        fas2= fas2
                    )),
                        shell=True,
                        stdout=PIPE,
                        stderr=PIPE,
                        env=my_env
                    )
                    output,err = proc.communicate()
                    #restore the context
                    chdir(self.context)
                    if err:
                        self.errlog('error for %s, %s' % (self.FG.G2U(mp),self.FG.G2U(p)))
                        self.errlog(err)
                    if output:
                        self.log('log for %s, %s' % (self.FG.G2U(mp),self.FG.G2U(p)))
                        self.log(output)
                except KeyboardInterrupt as kie:
                    self.errlog(str(kie), stdout=True)
                    self.errlog('user stop program when running %s, %s' %(mp, p), stdout=True)
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                except Exception as e:
                    self.errlog(str(e), stdout=True)
                    self.errlog('skip modeling %s v.s. %s' % (mp, p), stdout=True)
                chdir(self.context)
        print 'done!'
        
    def test(self):
        self.setFastaGraber()
        #in test session we just try PPI for FGFR3
        self.context=getcwd()
        my_env = environ.copy()
        for target in self.ppi['FGFR1']:
            fas1 = self.FG.grabPathByGene('FGFR1')
            fas2 = self.FG.grabPathByGene(target)
            #change to interpred context
            chdir('/home/limin/limin/InterPred/interpred/')
            call(' '.join( self.arrangeCall(
                fas1= fas1,
                fas2= fas2
            )),shell=True, env=my_env)
            #restore the context
            chdir(self.context)
        print 'done!'
    def singletest(self, a='FGFR1', b='PIK3R1'):
        self.setFastaGraber()
        #in test session we just try PPI for FGFR3
        self.context=getcwd()
        my_env = environ.copy()
        #select only one case to simulate
        fas1 = self.FG.grabPathByGene(a)
        fas2 = self.FG.grabPathByGene(b)
        #change to interpred context
        chdir('/home/limin/limin/InterPred/interpred/')
        call(' '.join( self.arrangeCall(
            fas1= fas1,
            fas2= fas2
        )),shell=True, env=my_env)
        #restore the context
        chdir(self.context)
        print 'done!'
    def cmdstring(self, a='FGFR1', b='PIK3R1'):
        self.setFastaGraber()
        self.context=getcwd()
        print ' '.join( self.arrangeCall( 
            fas1 = self.FG.grabPathByGene(a),
            fas2 = self.FG.grabPathByGene(b)
        ))
        
if __name__ == '__main__':
    import sys
    sklist=[]
    sklist2=[]
    dp = dispatcher(open(sys.argv[1]))
    sklist=open('./done.csv').read().split('\n')
    sklist=map(lambda x: x.split(','), sklist)
#    sklist2=open('./skip.csv').read().split('\n')
#    sklist2=map(lambda x: x.split(','), sklist2)
#    dp.singletest('EGFR','ABL2')
#    dp.cmdstring('ERBB2','ABL1')
    dp.run(skipList=sklist + sklist2)
