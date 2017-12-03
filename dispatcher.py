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
    def setFastaGraber(self,repo='./flattened',
    mapping='./uniprot_mapping.csv'):
        self.FG = FastaGraber.FastaGraber(repo=repo,mapping=mapping)
        return
    def arrangeCall(self,fas1,fas2,cpu=32):
        return [self.interpred_use_python, 
            self.interpred_executable,
            '-fasta',
            self.context + '/' + fas1,
            self.context + '/' + fas2,
            '-cpu',
            str(cpu)
        ]
    def log(self,msg, filename='./log'):
        f = open(self.context + '/' + filename, 'a')
        f.write('#'*10 + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + '#'*10 + '\n')
        f.write(msg + '\n')
    def errlog(self,msg ,filename='./errlog'):
        f = open(self.context + '/' + filename, 'a')
        f.write('#'*10 + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + '#'*10 + '\n')
        f.write(msg + '\n')
    def run(self, skipList=[]):
        def done(p1,p2):
            p1 = p1.split('/')[2].split('.')[0]
            p2 = p2.split('/')[2].split('.')[0]
            print 'check done %s, %s'% (p1,p2)
            for i in skipList:
                if i[0] == p1 and i[1] == p2:
                    print 'done %s, %s', (p1,p2)
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
                print str(e)
                print 'skip modeling %s v.s. *' % mp
                self.errlog(str(e))
                self.errlog('skip modeling %s v.s. *' % mp)
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
                    if err:
                        self.errlog('error for %s, %s' % (mp,p))
                        self.errlog(err)
                    if output:
                        self.log('log for %s, %s' % (mp,p))
                        self.log(output)
                except KeyboardInterrupt as kie:
                    print str(kie)
                    print 'user stop program when running %s, %s' %(mp, p)
                    self.errlog('user stop program when running %s, %s' %(mp, p))
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                except Exception as e:
                    print str(e)
                    print 'skip modeling %s v.s. %s' % (mp, p)
                    self.errlog(str(e))
                    self.errlog('skip modeling %s v.s. %s' % (mp, p))
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
        
if __name__ == '__main__':
    dp = dispatcher(open('./interactions.csv'))
#    sklist=open('./done.csv').read().split('\n')
#    sklist=map(lambda x: x.split(','), sklist)
    dp.singletest('ERBB2','ABL1')
