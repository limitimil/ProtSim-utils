import PPIReader
import FastaGraber
import csv
import os
import glob
import sys
class scoreCollector(PPIReader.PPIReader):
    def __init__(self, fromPath='./out'):
        self.fromPath=fromPath
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
if __name__ == '__main__':
    sc = scoreCollector(
        fromPath='/home/limin/limin/InterPred/out1110',
    )
    sc.makeTable()
        
