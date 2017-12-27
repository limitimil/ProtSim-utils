from subprocess import Popen, PIPE
import sys
import glob
from os import environ
class RosettaGraber(object):
    def __init__(self, interpred_path='./output_files'):
        self.scripts = self.collect(interpred_path)
    def collect(self, p):
        fn = glob.glob('%s/*rosetta.sh' % p)
        return fn
    @staticmethod
    def caller(s):
        my_env = environ.copy()
        proc = Popen(' '.join(['sh',s]), shell=True, stdout=PIPE, stderr=PIPE,
        env=my_env)
        output, err = proc.communicate()
        return output, err
        
        
if __name__ == '__main__':
    rg = RosettaGraber(interpred_path=sys.argv[1])
    print '\n'.join(rg.scripts)
