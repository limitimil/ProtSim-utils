import os
import sys
import csv
class FastaGraber(object):
    repo='./flattened'
    mapping='./uniprot_mapping.csv'
    def __init__(self, repo='./flattened', mapping='./uniprot_mapping.csv'):
        self.repo=repo
        self.mapping=mapping
        if not self.check_repo():
            sys.stderr.write('[%s] your repository directory is wrong\n' %
            self.__class__.__name__)
        if not self.check_mapping():
            sys.stderr.write('[%s] your mapping file is wrong\n' %
            self.__class__.__name__)
    def check_repo(self):
        if os.path.isdir(self.repo):
            return True
        return False
    def check_mapping(self):
        if os.path.isfile(self.mapping):
            return True
        return False
    def grabPathByUID(self, Uid): #grab fasta path by uniprot id
        target= '/'.join([self.repo, Uid+'.fasta'])
        if os.path.isfile(target):
            return target
        raise Exception('fasta file %s not found' % target)
    def grabPathByGene(self, Gene):
        target =self.G2U(Gene)
        return self.grabPathByUID(target)
    def G2U(self,Gene):
        tab=csv.reader(open(self.mapping), delimiter=',')
        tab=list(tab)
        label, tab= tab[0], tab[1:]
        for t in tab:
            if Gene==t[0]:
                return t[2]
        raise Exception('Gene name [%s] does not include in the mapping file' %
        Gene)
    def U2G(self,Uid):
        tab=csv.reader(open(self.mapping), delimiter=',')
        tab=list(tab)
        label, tab= tab[0], tab[1:]
        for t in tab:
            if Uid==t[2]:
                return t[0]
        raise Exception('Uniprot ID [%s] does not include in the mapping file' %
        Uid)
if __name__ == '__main__':
    fg = FastaGraber()
    print fg.G2U('KDR')
    print fg.U2G('VGFR3_HUMAN')
    print fg.grabPathByGene('VEGFC')
    print fg.grabPathByGene('fail')
