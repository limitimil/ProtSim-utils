import os, re
def make_rosetta_script(filepath, coarse_models_files):
    def rosetta_string(s):
        return s % (ROSETTA + 'source/bin', 
        ROSETTA+'source/bin/relax.static.linuxgccrelease', 
        ROSETTA+'database'
        )

    ROSETTA =\
    "/home/limin/limin/Rosetta/rosetta_bin_linux_2017.39.59729_bundle/main/"


    rosetta_script_name = filepath
    rosetta_script = open(rosetta_script_name, 'w')

    rosetta_script.write(rosetta_string("#!/bin/bash\nROSETTABIN=\"%s\"\n"
                         "ROSETTARELAX=\"%s\"\n"
                         "ROSETTADB=\"%s\"\n"))
    rosetta_script.write(
                         "OUTPUTDIR=\"./docking_models\"\n"
                         "DBPARA=\"-database $ROSETTADB\"\n"
                         "PARTNERSPARA=\"-docking:partners A_B\"\n"
                         "OTHERPARA=\"-ignore_zero_occupancy\"\n"
                         "OUTPUTPARA=\"-out:file:silent $OUTPUTDIR/$base.silent  -out:file:scorefile $OUTPUTDIR/$base.sc\"\n"
                         "DOCKPARA=\"-dock_pert 5 12 -nstruct 1000\"\n\n")

    for coarse_model_file in coarse_models_files:
        base = os.path.splitext(os.path.basename(coarse_model_file))[0]
        rosetta_script.write("$ROSETTARELAX -database $ROSETTADB -in:file:s " + coarse_model_file + " -relax:constrain_relax_to_start_coords -nstruct 1 -out:pdb -out:path:pdb $OUTPUTDIR\n"
                             "$ROSETTABIN/docking_protocol.static.linuxgccrelease $DBPARA -in:file:s $OUTPUTDIR/" + base + "_0001.pdb "
                             "-out:file:silent $OUTPUTDIR/" + base + ".silent  -out:file:scorefile $OUTPUTDIR/" + base + ".sc $PARTNERSPARA $DOCKPARA $OUTPUTPARA $OTHERPARA\n")
    rosetta_script.close()
class ScriptComposer(object):
    def __init__(self, outpath = './out'):
        assert(os.path.isdir(outpath))
        self.outpath = outpath
    def rosetta(self, ProtA, ProtB, CoarseModels):
        assert(re.search('^[\w]+$',ProtA))
        assert(re.search('^[\w]+$',ProtB))
        
        filepath = os.path.join(
            self.outpath,
            '%s_%s_rosetta.sh' %(ProtA, ProtB)
        )
        CoarseModels = map(os.path.abspath, CoarseModels)
        make_rosetta_script(filepath, CoarseModels)
if __name__ == '__main__':
    import sys
    import csv
    assert(len(sys.argv) == 2)
    tab = csv.DictReader(open(sys.argv[1]),delimiter=',')
    mapper = {}
    for t in tab:
        mapper[(t['protein_A'],t['protein_B'])]=\
            mapper.get((t['protein_A'],t['protein_B']),[]) + [t['modelname']]
        
    SC = ScriptComposer(outpath = './out.1221')
    for k, v in mapper.items():
        SC.rosetta(k[0],k[1],v)
    print 'done!'
    
