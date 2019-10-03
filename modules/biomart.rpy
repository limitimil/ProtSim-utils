library("biomaRt")

ensembl <- useMart("ensembl",dataset="hsapiens_gene_ensembl")

ocp <- read.csv(file="{input_file_path}", header=TRUE, sep=",")

result <- getBM(attributes=c("external_gene_name","ensembl_peptide_id"), filters="external_gene_name", values=ocp$Gene, mart=ensembl)

result = result[result$ensembl_peptide_id!="",]

# You can change to filename to save the file into different file path
output_filename="{output_file_path}"
write.table(result, file=output_filename, sep=",", row.names=F)
