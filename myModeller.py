import os
from Bio.SeqIO import PirIO
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
class PirWriter(PirIO.PirWriter):
    def write_record(self, record):
        from Bio.Alphabet import single_letter_alphabet, generic_protein,\
        generic_dna, generic_rna
        from Bio.SeqIO.PirIO import _pir_alphabets
        """Write a single PIR record to the file."""
        assert self._header_written
        assert not self._footer_written
        self._record_written = True

        if self.record2title:
            title = self.clean(self.record2title(record))
        else:
            title = self.clean(record.id)

        if record.name and record.description:
            description = self.clean(record.description)
        elif record.name and not record.description:
            description = self.clean(record.name)
        else:
            description = self.clean(record.description)

        if self.code:
            code = self.code
        else:
            if isinstance(record.seq.alphabet, type(generic_protein)):
                code = "P1"
            elif isinstance(record.seq.alphabet, type(generic_dna)):
                code = "D1"
            elif isinstance(record.seq.alphabet, type(generic_rna)):
                code = "RL"
            else:
                code = "XX"

        assert code in _pir_alphabets, "Sequence code must be one of " + \
                                       _pir_alphabets.keys() + "."
        assert "\n" not in title
        assert "\r" not in description

        self.handle.write(">%s;%s\n%s\n" % (code, title, description))

        data = self._get_seq_string(record)  # Catches sequence being None

        assert "\n" not in data
        assert "\r" not in data

        if self.wrap:
            line = ""
            for i in range(0, len(data), self.wrap):
                line += data[i:i + self.wrap] + "\n"
            line = line[:-1] + "*\n"
            self.handle.write(line)
        else:
            self.handle.write(data + "*\n")
class modeller(object):
    pir = None
    template = None
    def __init__(self, pdbdir='./'):
        self.pdbdir = pdbdir
    def run(self, seqId):
        assert(self.check(seqId))
        from modeller import log, environ
        from modeller.automodel import automodel

        #log.verbose()
        #log.none()
        log.level(output=0, errors=0, notes=0, warnings=0, memory=0)
        env = environ()
        env.io.atom_files_directory = [self.template[0]]

        a = automodel(env,
            alnfile = self.pir,
            knowns = self.template[1],
            sequence = seqId
        )
        a.auto_align()
        a.make()
        fn = '{}.B99990001.pdb'.format(seqId)
        assert(os.path.isfile(fn))
        return os.path.abspath(fn)
    def pushPir(self, fn):
        assert(os.path.isfile(fn))
        self.pir = fn
    def pushTemplateFile(self, fn):
        if not os.path.isfile(fn):
            raise Exception('file {} not found'.format(fn))
        self.template = (os.path.dirname(fn),
        os.path.splitext(os.path.basename(fn))[0])
    def validate(self):
        if not self.pir or not self.template:
            return False
        #there are at least 2 sequence in pirfile
        pir = list(SeqIO.parse(self.pir,'pir'))
        structure_templates = filter(
            lambda x: x.description.startswith('structureX'),
            pir)
        if not len(pir) >= 2:
            return False
        if not structure_templates:
            return False
        #the strucure based sequence in pirfile should be retreivable in pir file
        pdbnames = map( lambda x: x.description.split(':')[1].strip(),
            structure_templates)
        if self.template[1] not in pdbnames:
            return False
        return True
    def check(self, seqId):
        pir = list(SeqIO.parse(self.pir,'pir'))
        find = filter(
            lambda x:True if x.id == seqId else False,
            pir)
        return bool(find)
def prepare_modeling(Fasta, PDB, chain):
    target = list(SeqIO.parse(Fasta,'fasta'))[0]
    target.id = os.path.splitext(os.path.basename(Fasta))[0]
    target.description = ':'.join([
        'sequence',
        target.id,
        'FIRST',
        '',
        'LAST',
        '',
        os.path.abspath(Fasta),
        target.description,
        '',
        ''
    ])
    template = SeqRecord(seq=Seq(''))
    template.id = os.path.splitext(os.path.basename(PDB))[0] 
    template.description = ':'.join([
        'structureX',
        template.id,
        'FIRST',
        chain,
        'LAST',
        chain,
        os.path.abspath(PDB),
        '',
        '',
        ''
    ])
    #save
    fn = '{}-{}.ali'.format(target.id,template.id)
    writer = PirWriter(open(fn,'w'),code = 'P1')
    writer.write_file([target, template])

    return {'target': target.id, 'template': template.id, 'alnfile':
    os.path.abspath(fn)}
def demo0201(target, template, chain):
    prepare = prepare_modeling(target, template, chain)
    so = modeller()
    so.pushPir(prepare['alnfile'])
    so.pushTemplateFile(template)
    print so.validate()
    print so.run(prepare['target'])
    print so.validate()
    print 'done'
