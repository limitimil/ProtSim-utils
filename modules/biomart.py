from rpy2 import robjects
import os


RPY_PATH = os.path.join( os.path.dirname(os.path.realpath(__file__)), 'biomart.rpy' )

class Biomart:
    def __init__(self,
            input_file_path = 'OCP/ocp.csv',
            output_file_path= 'STRING/gene_name_mapping.csv'):
        self.parameter = {
            'input_file_path' : input_file_path,
            'output_file_path' : output_file_path
        }
        self.script = open(RPY_PATH).read()
    def execute(self):
        return robjects.r(self.script.format(
            ** self.parameter
        ))

    @property
    def in_string(self):
        return self.script.format( ** self.parameter )


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        sys.stderr.write('You should put at least 2 parameters!')
        exit(1)
    bm = Biomart(sys.argv[1], sys.argv[2])
    print(bm.in_string)
    bm.execute()
    sys.stdout.write('done!')

