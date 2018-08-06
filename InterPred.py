import os
from sys import path
from subprocess import Popen,PIPE
class InterPred(object):
    ###########################################################################################
    BASE = "/home/limin/limin/InterPred/interpred"
    PDB = "/home/limin/disk2/RCSB_PDB/data/structures/divided/pdb"
    ###########################################################################################
    MODELLER_PYTHON = "/home/limin/bin/modeller9.15/bin/modpy.sh python2.7"
    scripts = {
        "entry":"InterPred.py",
        "submodule":{
            "make_coarse_models": "scripts/make_coarse_models.py",
            "make_homology_model":"scripts/make_homology_model.py",
            "make_structural_alignments":"scripts/make_structural_alignments.py"
        }
    }
    old_env=None
    old_path=None
    def msg(self, msg):
        print '#'*10+'InterPred Handler'+'#'*10
        print msg
    def call(self,cmdstring):
        self._env_set()
        try:
            proc=Popen(cmdstring,shell=True,stdout=PIPE,stderr=PIPE,env=os.environ)
            ret = proc.communicate()
        except Exception as e:
            self.msg(str(e))
            self._env_restore()
            return (None, str(e))
        self._env_restore()
        return ret
    def _env_restore(self):
        if self.old_env:
            os.environ=self.old_env
        if self.old_path:
            os.chdir(self.old_path)
        self.old_env = None
        self.old_path = None
        return
    def _env_set(self):
        if self.old_env or self.old_path:
            return
        #backup your environ
        self.old_env=os.environ.copy()
        self.old_path=os.getcwd()
        #Setup your Rosetta path
        os.environ["ROSETTAMAIN"] =\
        "/home/limin/limin/Rosetta/rosetta_bin_linux_2017.39.59729_bundle/main/"

        #Setup your HH suite and Modeller here if you want to do homology modelling################
        os.environ["HHDIR"] = "/home/limin/limin/HHsuite/install"
        os.environ["HHUTIL"] = "/home/limin/limin/HHsuite/install/scripts/"
        os.environ["HHPDB"] = "/home/limin/disk2/HHsuiteDB/PDB/pdb70"
        os.environ["HHUNI"] =\
        "/home/limin/disk2/HHsuiteDB/Uniprot/uniprot20_2013_03/uniprot20_2013_03"
        os.environ["PYTHONPATH"] = "/home/limin/bin/modeller9.15/modlib:" + str(os.getenv("PYTHONPATH"))
        ###########################################################################################

        TMP = self.BASE + "/tmp" #Temporary data folder
        DB = self.BASE + "/databases/"
        OUT = self.BASE + "/output_files"
        MODELS = self.BASE + "/homology_models"
        SCRIPTS = self.BASE + "/scripts"
        RFC = self.BASE + "/RandomForest"
        TM = SCRIPTS + "/TMalignChain"

        path.append(SCRIPTS)

        os.environ['BASE'] = self.BASE
        os.environ['TMPDIR'] = TMP
        os.environ['MODELS'] = MODELS
        os.environ['SCRIPTS'] = SCRIPTS
        os.environ['DB'] = DB
        os.environ['PDB'] = self.PDB
        os.environ['RFC'] = RFC
        os.environ['TMP'] = TMP
        os.environ['TM'] = TM
        os.environ['OUT'] = OUT
        #CPU cout be set in original InterPred Entry
        #Set a default value to make submodule run properly.
        os.environ['CPUS'] = '4'
        
        os.chdir(self.BASE)
    def classical_call(self, fas1, fas2, cpu=32):
    #be careful, you should put absolute path in fas1 and fas2 to avoid error
        return ' '.join([
            self.MODELLER_PYTHON,
            self.scripts['entry'],
            '-fasta',
            fas1,
            fas2,
            '-cpu',
            str(cpu)
        ])
    def submodule_call(self, modulename, args=''):
        if isinstance(args, list):
            return ' '.join([
                self.MODELLER_PYTHON,
                self.scripts['submodule'][modulename],
            ]+args)
        elif isinstance(args, str):
            return ' '.join([
                self.MODELLER_PYTHON,
                self.scripts['submodule'][modulename],
                args
            ])
            
