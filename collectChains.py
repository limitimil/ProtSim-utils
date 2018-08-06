from Bio.PDB.PDBParser import PDBParser
from Bio.PDB.PDBIO import PDBIO
import os
import sys
import errno
from EvalFunctions import evaluation
class chainParser:
    @staticmethod
    def getChains(s):
        #this function will help you parse the file name like:
        #EGFR_HUMAN_0___ABL1_HUMAN_0___pdb1fpu_B_pdb1fpu_A.pdb
        ret = s.split('___')[:2]
        assert(len(ret) == 2)
        return ret
        
class collectChains(object):
    def __init__(self, outpath='./out', inpath='./in'):
        #check outpath is valid, this script won't automatically generate the
        #out path. Here, two listdir call will evoke OS Exception when the
        #given path is not a folder
        os.listdir(outpath)
        files = os.listdir(inpath)
        #show pdb files in inpath
        files = filter(lambda x: x if x.endswith('.pdb') else None,
            files)
        print 'there are %s PDB files under input path' % len(files)
        sys.stdout.flush()
        sys.stdout.flush()
        self.outpath = outpath
        self.inpath = inpath
        self.files = files
    def collect(self, checkboard = []):
        if not checkboard:
            self.collect_0()
        self.collect_1(checkboard)
    def then_do(self, f):
        pass
    def collect_1(self, checkboard = []):
        def getChains(s):
            ret = s.split('___')[:2]
            assert(len(ret) == 2)
            return ret
        parser = PDBParser()
        io = PDBIO()
        for f in self.files:
            if not checkboard:
                break
            if f not in checkboard:
                continue
            try:
                os.mkdir(os.path.join( self.outpath, f))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            structure = parser.get_structure(f, os.path.join(self.inpath, f))
            chain_A, chain_B = getChains(f)
            io.set_structure(structure[0]['A'])
            io.save(os.path.join(self.outpath,f,chain_A + '.pdb'))
            io.set_structure(structure[0]['B'])
            io.save(os.path.join(self.outpath,f,chain_B + '.pdb'))
            #make this module can be reuse to other application
            self.then_do(f)
            #remove the finished file from checkboard
            checkboard.remove(f)
        
    def collect_0(self):
        def getChains(s):
            ret = s.split('___')[:2]
            assert(len(ret) == 2)
            return ret
        parser = PDBParser()
        io = PDBIO()
        for f in self.files:
            try:
                os.mkdir(os.path.join( self.outpath, f))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            structure = parser.get_structure(f, os.path.join(self.inpath, f))
            chain_A, chain_B = getChains(f)
            io.set_structure(structure[0]['A'])
            io.save(os.path.join(self.outpath,f,chain_A + '.pdb'))
            io.set_structure(structure[0]['B'])
            io.save(os.path.join(self.outpath,f,chain_B + '.pdb'))
            self.then_do(f)
class FiberDockRender(collectChains):
    fd_str = """
~/FiberDock1.1/addHydrogens.pl {chaina}.pdb {chainb}.pdb
cat {chainb}.pdb | grep ATOM | grep ' CA ' > {chainb}.ca.pdb
cat {chaina}.pdb | grep ATOM | grep ' CA ' > {chaina}.ca.pdb
~/FiberDock1.1/nma {chainb}.ca.pdb {chainb}.ca.nma 50 3 5.5 
~/FiberDock1.1/nma {chaina}.ca.pdb {chaina}.ca.nma 50 3 5.5 
~/FiberDock1.1/buildFiberDockParams.pl {chaina}.pdb.HB {chainb}.pdb.HB B B AA zero.trans resultFile 1 1000 0.85 1 glpk paramsFile 0.5 {chaina}.ca.pdb {chaina}.ca.nma {chainb}.ca.pdb {chainb}.ca.nma
~/FiberDock1.1/FiberDock paramsFile"""
    def then_do(self, f):
        def getChains(s):
            ret = s.split('___')[:2]
            assert(len(ret) == 2)
            return ret
        chain_A, chain_B = getChains(f)
        open(os.path.join(self.outpath, f, 'fd.sh'),'wb').write(self.fd_str.format(chaina=chain_A, chainb=chain_B))
        open(os.path.join(self.outpath, f, 'zero.trans'),'wb').write('1 0 0 0 0 0 0')
        return
class FiberDockScore:
    def __init__(self, inpath='./in'):
        #check outpath is valid, this script won't automatically generate the
        #out path. Here, two listdir call will evoke OS Exception when the
        #given path is not a folder
        files = os.listdir(inpath)
        #show pdb files in inpath
        files = filter(lambda x: x if x.endswith('.pdb') else None,
            files)
        print 'there are %s PDB files under input path' % len(files)
        sys.stdout.flush()
        sys.stdout.flush()
        self.inpath = inpath
        self.files = files
    def collect(self, outfile):
        if not outfile:
            outfile = sys.stdout
        #title
        outfile.write(','.join([
            'chainA',
            'chainB',
            'score'
        ]))
        outfile.write('\n')
        for  f in self.files:
            chain_A, chain_B = chainParser.getChains(f)
            score = evaluation(os.path.join(self.inpath,f,'resultFile.ref'))
            assert(len(score) == 1)
            score = score[0][1]
            outfile.write(','.join([
                chain_A,
                chain_B,
                score
            ]))
            outfile.write('\n')
if __name__ == '__main__':
    if len(sys.argv) < 3:
        Exception(
"""This script need 2 argument to run.
First for intput path, Second for output path
""")
    checkboard = []
    if len(sys.argv) > 3:
        checkboard = open(sys.argv[3]).read().split('\n')
#    cc = collectChains(inpath = sys.argv[1],outpath = sys.argv[2])
    cc = FiberDockRender(inpath = sys.argv[1],outpath = sys.argv[2])
    cc.collect(checkboard = checkboard)
        

