from StringIO import StringIO
import csv
class PPIReader(object):
    def __init__(self, csvStream):
        s = csvStream.read()
        s = s.split('\n')
        s = filter(
            lambda x: x if not x.startswith('#') else None,
            s
        )
        s = '\n'.join(s)
        rows = list(csv.reader(StringIO(s), delimiter=','))
        self.ppi={}
        for r in rows:
            if len(r) < 2:
                continue
            self.ppi[r[0]] = r[1:]
    def flattened(self):
        ret = [] 
        for k, proteins in self.ppi.items():
            for p in proteins:
                ret.append([k, p])
        return ret
    def participant(self):
        major = self.ppi.keys()
        partner = []
        for v in self.ppi.values():
            partner += v
            
        return list(set(major + partner))
    def uniq(self):
        for k in self.ppi.keys():
            self.ppi[k] = list(set(self.ppi[k]))
    def write(self, outfile):
        with open(outfile,'w') as f:
            for k,v in self.ppi.items():
                f.write(','.join([k]+v))
                f.write('\n')
        return 
if __name__ == '__main__':
    pr = PPIReader(open('./interactions5.csv'))
    print '\n'.join(map(lambda x: ','.join(x), pr.flattened()))

