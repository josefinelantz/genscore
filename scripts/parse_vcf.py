# scripts/parse_vcf.py

from cyvcf2 import VCF
import pandas as pd
import os

# All possible consequence types (SO-terms) fetched from Ensembl release 113 (November 2024).
# The consequence types are ordered by their severeness lower index more severe
# https://www.ensembl.org/info/genome/variation/prediction/predicted_data.html

# TODO - Move this list to a separate file 

CONSEQUENCE_ORDER = [
    "transcript_ablation",
    "splice_acceptor_variant", 
    "splice_donor_variant", 
    "stop_gained",         
    "frameshift_variant",
    "stop_lost",
    "start_lost",
    "transcript_amplification",
    "feature_elongation",
    "feature_elongation",
    "inframe_insertion",
    "inframe_deletion",
    "missense_variant",
    "protein_altering_variant",
    "splice_donor_5th_base_variant",
    "splice_region_variant",
    "splice_donor_region_variant",
    "splice_polypyrimidine_tract_variant",
    "incomplete_terminal_codon_variant",
    "start_retained_variant",
    "stop_retained_variant",
    "synonymous_variant",
    "coding_sequence_variant",
    "mature_miRNA_variant",
    "5_prime_UTR_variant",
    "3_prime_UTR_variant",
    "non_coding_transcript_exon_variant",
    "intron_variant",
    "NMD_transcript_variant",
    "non_coding_transcript_variant",
    "coding_transcript_variant",
    "upstream_gene_variant",
    "downstream_gene_variant",
    "TFBS_ablation",
    "TFBS_amplification",
    "TF_binding_site_variant",
    "regulatory_region_ablation",
    "regulatory_region_amplification",
    "regulatory_region_variant",
    "intergenic_variant",
    "sequence_variant",
    "not_reported"
]

def csq_to_dict(csq_fields, variant_csq):
    fields = variant_csq.split(",")[0].split("|")
    return dict(zip(csq_fields, fields))

def scores_to_dict(score_categories, variant_rank_result):
    category_scores = [float(x) for x in variant_rank_result.split("|")]
    return dict(zip(score_categories, category_scores))


def parse_vcf(vcf_file):
    """ Parses vcf_file using cyvcf2 
        Parameters: (str): path to pre-processed VCF file containing somatic SNVs scored with Genmod. 
        Returns: A Pandas DataFrame with extracted data.  
    """
    # Read VCF file into a VCF-object
    vcf = VCF(vcf_file)

    # Get the fields present in INFO["CSQ"] for this VCF
    csq_fields = vcf.get_header_type("CSQ")["Description"][51:].split("|")

    data = []
    #clin_sig = []
    #rank_result = []
    #rank_score = []
    
    for variant in vcf:
        chrom = variant.CHROM
        pos = variant.POS
        ref = variant.REF
        alt = variant.ALT[0]
        info = variant.INFO
        rank_result = info.get("RankResult", "0|0|0|0|0|0")
        rank_score = info.get("RankScore", "")[2:]
        af, pp, csq, vcqf, vaf, clnsig = rank_result.split("|")
        #rank_score = sum(map(float, rank_result.split("|")))
        clin_sig = info.get("CLNSIG", "not_reported")
        csq_dict = csq_to_dict(csq_fields, variant.INFO["CSQ"])
        data.append({
            "CHROM": chrom,
            "POS": pos,
            "REF": ref, 
            "ALT": alt,
            "CAT_AF_SCORE": float(af),
            "CAT_PP_SCORE": float(pp),
            "CAT_CSQ_SCORE": float(csq),
            "CAT_VCQF_SCORE": float(vcqf),
            "CAT_VAF_SCORE": float(vaf),
            "CAT_CLNSIG_SCORE": float(clnsig),
            "CLNSIG": clin_sig,
            "RankScore": float(rank_score),
            "RankResult": rank_result
        })
    
    df = pd.DataFrame(data)
    print(df.head)
    return df