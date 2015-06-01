#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from optparse import OptionParser
import sys
from rgt.ExperimentalMatrix import ExperimentalMatrix
from rgt.CoverageSet import CoverageSet
import numpy as np
import os
from rgt.GenomicRegionSet import GenomicRegionSet
from copy import deepcopy

def get_experimental_matrix(bams, bed):
    """Load artificially experimental matrix. Only genes in BED file are needed."""
    m = ExperimentalMatrix()
    
    m.fields = ['name', 'type', 'file']
    m.fieldsDict = {}
    
    names = []
    for bam in bams:
        n, _ = os.path.splitext(os.path.basename(bam))
        m.files[n] = bam
        names.append(n) 
    m.names = np.array(['housekeep'] + names)
    m.types = np.array(['regions'] + ['reads']*len(names))
    g = GenomicRegionSet('RegionSet')
    g.read_bed(bed)
    m.objectsDict['housekeep'] = g
    
    return m

def get_factor_matrix(d, colnames):
    """Give matrix describing factors between genes. Idealy, factors in a column should be approx. the same."""
    res = []
    
    original_f = get_factors(d)

    if d.shape[0] > 1 and d.shape[1] > 1:
        print("column/gene wise analysis")
        for i in range(d.shape[1]):
            data = deepcopy(d)
            data = np.delete(data, i, 1) #remove gene i
            f = get_factors(data)
            assert len(f) == len(original_f)
            res = sum(map(lambda x: (x[0]-x[1])**2, zip(original_f, f))) / float(len(f))
            
            
            print(colnames[i], i, res, f)
        print("")
        
        print("row/sample wise analysis")
        for i in range(d.shape[0]):
            data = deepcopy(d)
            data = np.delete(data, i, 0) #remove sample i
            f = get_factors(data)
            assert len(f) == len(original_f) - 1
            tmp = deepcopy(original_f)
            del tmp[i]
            assert len(f) == len(tmp)
            res = sum(map(lambda x: (x[0]-x[1])**2, zip(tmp, f))) / float(len(f))
            
            
            print(i, res, f)
        print("")
            
     
def output_R_file(name, res, colnames):
    """"Write R code to file to check whether genes give same signal among the samples"""
    f = open(name + 'norm.R', 'w')
    #output for R
    #everthing in one vector
    
    #if res.shape[1] > 0:
    l = reduce(lambda x, y: x+y, [map(lambda x: str(x), list(np.array(res[:,i]).reshape(-1,))) for i in range(res.shape[1])])
    #else:
    #    l = list(np.array(res.reshape(-1,)))
    
    print('d = c(', ', '.join(l), ')', sep='', file=f)
    print('d = matrix(d, %s)' %res.shape[0], file=f)
    print('names = c("', '", "'.join(colnames), '")', sep='', file=f)
    print('par(mar=c(15,5,5,5))', file=f)
    print('barplot(d, beside = TRUE, names.arg = names, las=2, main="Housekeeping Genes Ratio", ylab="Signal")', file=f)
    

def get_factors(data):
    #normalize: increase values to highest value
    d = deepcopy(data)  
    colmax = np.mean(d, axis=0)

    for i in range(d.shape[0]):
        for j in range(d.shape[1]):
            d[i,j] = colmax[:,j][0,0]/d[i,j]
    
    return list(np.array(np.mean(d, axis=1)).reshape(-1))

def norm_gene_level(bams, bed, name, verbose):
    """Normalize bam files on a gene level. Give out list of normalization factors."""
    m = get_experimental_matrix(bams, bed)
    
    d = zip(m.types, m.names)
    d = map(lambda x: x[1], filter(lambda x: x[0] == 'reads', d)) #list of names which are reads
    
    regions = m.objectsDict['housekeep'] #GenomicRegionSet containing housekeeping genes
         
    covs = []
    for cond in d:
        bam_path = m.files[cond]
        c = CoverageSet(cond, regions) 
        c.coverage_from_bam(bam_file=bam_path)
        c.genomicRegions.sort()
        covs.append(c)
    
    #create matrix sample x gene for signal
    signals = [[sum(covs[k].coverage[i])+1 for i in range(len(covs[k].genomicRegions))] for k in range(len(covs))]
    assert len(covs) > 0
    gene_names = [covs[0].genomicRegions[i].name for i in range(len(covs[0].genomicRegions))]
    
    colnames = gene_names
    d = np.matrix(signals, dtype=float)
    print("samples: %s" %",".join(map(lambda x: os.path.basename(x), bams)))
    print("Housekeeping gene matrix (columns-genes, rows-samples)")
    print(d)
    print("")
    
    if verbose:
        #output R code to check wether gene give same signal
        get_factor_matrix(d, colnames)
        #output_R_file(name, res, colnames)
    
    print("factors")
    return get_factors(d)
    

if __name__ == '__main__':
    #bams = ['/home/manuel/test1.bam', '/home/manuel/test2.bam']
    bams = ['/home/manuel/workspace/cluster_p/hematology/local/new_run/bam/32D_mm_BCRABL_H3K9ac_rep1.bam', '/home/manuel/workspace/cluster_p/hematology/local/new_run/bam/32D_mm_BCRABL_H3K9ac_rep2.bam', '/home/manuel/workspace/cluster_p/hematology/local/new_run/bam/32D_mm_BCRABL_IM_H3K9ac_rep1.bam', '/home/manuel/workspace/cluster_p/hematology/local/new_run/bam/32D_mm_BCRABL_IM_H3K9ac_rep2.bam', '/home/manuel/workspace/cluster_p/hematology/local/new_run/bam/32D_mm_JAK2VF_H3K9ac_rep1.bam', '/home/manuel/workspace/cluster_p/hematology/local/new_run/bam/32D_mm_JAK2VF_H3K9ac_rep2.bam', '/home/manuel/workspace/cluster_p/hematology/local/new_run/bam/32D_mm_JAK2VF_Rux_H3K9ac_rep1.bam', '/home/manuel/workspace/cluster_p/hematology/local/new_run/bam/32D_mm_JAK2VF_Rux_H3K9ac_rep2.bam', '/home/manuel/workspace/cluster_p/hematology/local/new_run/bam/32D_mm_LV_H3K9ac_forBCRABL_rep1.bam', '/home/manuel/workspace/cluster_p/hematology/local/new_run/bam/32D_mm_LV_H3K9ac_forBCRABL_rep2.bam', '/home/manuel/workspace/cluster_p/hematology/local/new_run/bam/32D_mm_LV_H3K9ac_forJAK2VF_rep1.bam', '/home/manuel/workspace/cluster_p/hematology/local/new_run/bam/32D_mm_LV_H3K9ac_forJAK2VF_rep2.bam']
    bed = '/home/manuel/workspace/cluster_p/hematology/exp/exp16_check_housekeeping_genes/pot_housekeeping_genes_mm9.bed'
    
    bams = ['/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/MPP_WT_H3K27ac_1.bam', '/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/MPP_WT_H3K27ac_2.bam', '/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/CDP_WT_H3K27ac_1.bam', '/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/CDP_WT_H3K27ac_2.bam']
    bed = '/home/manuel/pot_housekeeping_genes_hg19.bed'
    
    bams = ['/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC1_H3K27ac.bam', '/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC2_H3K27ac.bam', '/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC3_H3K27ac.bam', '/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC4_H3K27ac.bam', '/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC5_H3K27ac.bam', '/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/PBBA1_H3K27ac.bam', '/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/PBBA2_H3K27ac.bam', '/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/PBBA4_H3K27ac.bam']
    #bams = ['/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC1_H3K27ac.bam', '/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC2_H3K27ac.bam', '/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC4_H3K27ac.bam', '/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC5_H3K27ac.bam', '/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/PBBA1_H3K27ac.bam', '/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/PBBA2_H3K27ac.bam', '/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/PBBA4_H3K27ac.bam']
    #bams = ['/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/MPP_WT_H3K27ac_1.bam','/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/MPP_WT_H3K27ac_2.bam','/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/CDP_WT_H3K27ac_1.bam','/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/CDP_WT_H3K27ac_2.bam']
    
    b_nestler_H3K36me3_sal = ['/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/nestler/H3K36me3_sal_rep1.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/nestler/H3K36me3_sal_rep2.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/nestler/H3K36me3_sal_rep3.bam']
    b_nestler_H3K36me3_coc = ['/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/nestler/H3K36me3_coc_rep1.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/nestler/H3K36me3_coc_rep2.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/nestler/H3K36me3_coc_rep3.bam']
    
    b_nestler_H3K36me1_sal = ['/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/nestler/H3K4me1_sal_rep1.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/nestler/H3K4me1_sal_rep2.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/nestler/H3K4me1_sal_rep3.bam']
    b_nestler_H3K36me1_coc = ['/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/nestler/H3K4me1_coc_rep1.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/nestler/H3K4me1_coc_rep2.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/nestler/H3K4me1_coc_rep3.bam']
    
    b_zenke_MPP = ['/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/MPP_WT_H3K27ac_1.bam','/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/MPP_WT_H3K27ac_2.bam']
    b_zenke_CDP = ['/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/CDP_WT_H3K27ac_1.bam','/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/CDP_WT_H3K27ac_2.bam']
    b_zenke_cDC = ['/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/cDC_WT_H3K27ac_1.bam','/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/cDC_WT_H3K27ac_2.bam']
    b_zenke_pDC = ['/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/pDC_WT_H3K27ac_1.bam','/home/manuel/workspace/cluster_p/dendriticcells/local/zenke_histones/bam/pDC_WT_H3K27ac_2.bam']
    
    #hg19
    bed = '/home/manuel/pot_housekeeping_genes_hg19.bed'
    
    b_payton_CC = ['/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC1_H3K27ac.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC2_H3K27ac.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC3_H3K27ac.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC4_H3K27ac.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/CC5_H3K27ac.bam']
    b_payton_PBBA = ['/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/PBBA1_H3K27ac.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/PBBA2_H3K27ac.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/PBBA4_H3K27ac.bam']
    b_payton_FL = ['/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/FL1_H3K27ac.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/FL2_H3K27ac.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/FL5_H3K27ac.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/FL8_H3K27ac.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/FL10_H3K27ac.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/FL11_H3K27ac.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/FL14_H3K27ac.bam','/home/manuel/workspace/cluster_p/allhoff/project_THOR/data/payton/FL16_H3K27ac.bam']
    
    b_blueprint_H3K27ac_monocyte = ['/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C000S5H2_H3K27ac_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C0010KH1_H3K27ac_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C001UYH2_H3K27ac_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C004SQH1_H3K27ac_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00BWXH1_H3K27ac_monocyte.bam']
    b_blueprint_H3K27ac_macrophage = ['/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C005VGH1_H3K27ac_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S001S7H1_H3K27ac_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S0022IH1_H3K27ac_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00390H1_H3K27ac_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00BYTH1_H3K27ac_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00C0JH1_H3K27ac_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00NM5H1_H3K27ac_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00NN3H1_H3K27ac_macrophage.bam']
    b_blueprint_H3K4me1_monocyte = ['/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C000S5H2_H3K4me1_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C0010KH1_H3K4me1_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C001UYH2_H3K4me1_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C004SQH1_H3K4me1_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00BWXH1_H3K4me1_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00NJBH1_H3K4me1_monocyte.bam']
    b_blueprint_H3K4me1_macrophage = ['/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C005VGH1_H3K4me1_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S001S7H1_H3K4me1_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S0022IH1_H3K4me1_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00390H1_H3K4me1_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00BXVH1_H3K4me1_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00BYTH1_H3K4me1_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00C0JH1_H3K4me1_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00NK9H1_H3K4me1_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00NM5H1_H3K4me1_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00NN3H1_H3K4me1_macrophage.bam']
    b_blueprint_H3K4me3_monocyte = ['/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C000S5H2_H3K4me3_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C0010KH1_H3K4me3_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C001UYH2_H3K4me3_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C004SQH1_H3K4me3_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00BWXH1_H3K4me3_monocyte.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00NJBH1_H3K4me3_monocyte.bam']
    b_blueprint_H3K4me3_macrophage = ['/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/C005VGH1_H3K4me3_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S001S7H1_H3K4me3_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S0022IH1_H3K4me3_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00390H1_H3K4me3_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00BXVH1_H3K4me3_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00BYTH1_H3K4me3_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00C0JH1_H3K4me3_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00NK9H1_H3K4me3_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00NM5H1_H3K4me3_macrophage.bam','/home/manuel/workspace/cluster_p//blueprint/raw/new_run/bams/S00NN3H1_H3K4me3_macrophage.bam']
    
    
    print(norm_gene_level(b_payton_FL + b_payton_CC, bed, 'testname', True))
    
    #awk -vOFS='\t' '$5=="+" {print $1,$2-500,$2,$4,$5} $5=="-" {print $1,$3,$3+500,$4,$5}'
    
    
    
    