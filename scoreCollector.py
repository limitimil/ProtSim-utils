import re
import PPIReader
import FastaGraber
import csv
import os
import glob
import sys
class scoreCollector(FastaGraber.FastaGraber):
    def __init__(self, fromPath='./out'):
        self.fromPath=fromPath
        super(scoreCollector, self).__init__()
    def makeTable(self, donefile='./done.csv'):
        def getTopScore(fn):
            a=open(fn).readline().split()
            assert(len(a) == 3)
            return a
        if not donefile:
            raise Exception(
'done file has not set, this module has not designed to support no done file retrieving.')
        with open(donefile) as csvfile:
            result = csv.reader(csvfile,delimiter=',')
            result = list(result)
        writer = csv.writer(sys.stdout)
        writer.writerow([
            'filename',
            'protein_A',
            'protein_B',
            'template_A',
            'template_B',
            'topInterPredScore',
        ])
        for r in result:
            fn = glob.glob('%s/%s*%s*predictions'%(self.fromPath, r[0], r[1]) )
            for f in fn:
                try:
                    ts = getTopScore(f)
                    writer.writerow([
                        f,
                        r[0], r[1],
                        ts[0], ts[1],
                        ts[2]
                    ])
                except AssertionError as e:
                    sys.stderr.write(str(e))
                    sys.stderr.write('skip %s' % str(f))
                    sys.stderr.write('\n')
        return
    def makeDonefile(self, outfile=None):
        if not outfile:
            outfile = sys.stdout
        fn = glob.glob('%s/*rosetta.sh' % self.fromPath)
        for f in fn:
            f = os.path.basename(f)
            ppi = re.split('___', f)[:2]
            ppi[0] =re.sub('_\d','', ppi[0])
            ppi[1] =re.sub('_\d','', ppi[1])
            outfile.write(','.join(ppi) + '\n')
        return
    def makeInteraction(self, donefile='./done.csv', outfile=None):
        if not outfile:
            outfile = sys.stdout
        with open(donefile) as csvfile:
            result=csv.reader(csvfile, delimiter=',')
            result = list(result)
        interaction = {}
        for r in result:
            try:
                interaction[self.U2G(r[0])] = interaction.get(self.U2G(r[0]), [])+\
                [self.U2G(r[1])]
            except Exception as e:
                print str(e)
                print 'pass no mapping interaction'
        for k,v in interaction.items():
            outfile.write(','.join([k] + v))
            outfile.write('\n')
        if outfile!= sys.stdout:
            outfile.close()
        return

        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        sc = scoreCollector(
            fromPath=sys.argv[1],
        )
    else:
        sc = scoreCollector(
            fromPath='/home/limin/limin/InterPred/interpred/output_files',
        )
#    ff = open('./done.csv', 'w')
#    sc.makeDonefile(outfile=ff)
    sc.makeDonefile()
#    ff.close()
#    sc.makeInteraction(donefile='tmp.1126')
       
