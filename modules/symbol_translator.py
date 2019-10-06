from rpy2 import robjects
from rpy2.robjects.conversion import localconverter
from rpy2.robjects import pandas2ri
ENSEMBL = robjects.r(
"""
    library('biomaRt')
    ensembl <- useMart('ensembl',dataset='hsapiens_gene_ensembl')
"""
)
BIOMART_FUNCTION = robjects.r(
"""
function( ids, ensembl_object , filter= 'external_gene_name'){
    library('biomaRt')
    result <- getBM(attributes=c('external_gene_name','ensembl_peptide_id'), 
        filters=filter, 
        values=ids, 
        mart=ensembl_object)
    result <- result [ 
        apply( result, 1, function(x) {all(x!='')}) ,]
}
"""
)
def py2r_string(s: str):
    return robjects.StrVector((s,))[0]
class SymbolTranslator:
    supported_identifier = ["external_gene_name","ensembl_peptide_id"]
    @staticmethod
    def translator(ids, identifier):
        if identifier not in SymbolTranslator.supported_identifier:
            raise RuntimeError('not supported identifer: {}'.format(identifier))
        result = BIOMART_FUNCTION(
                robjects.StrVector(ids), 
                ENSEMBL, 
                filter=py2r_string(identifier)
                )
        with localconverter(robjects.default_converter + pandas2ri.converter):
            result = robjects.conversion.rpy2py(result)
        return result
            

    
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        sys.stderr.write('Please input at least one gene symbol in the arguments')
    result = SymbolTranslator.translator(sys.argv[1:],"external_gene_name")
    print(result)
