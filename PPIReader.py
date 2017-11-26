from StringIO import StringIO
import csv
class PPIReader:
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
if __name__ == '__main__':
    pr = PPIReader(open('./interactions.csv'))
    print pr.ppi
    print '\n'.join(map(str, pr.flattened()))
