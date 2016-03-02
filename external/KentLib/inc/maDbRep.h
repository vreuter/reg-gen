/*****************************************************************************
 * Copyright (C) 2000 Jim Kent.  This source code may be freely used         *
 * for personal, academic, and non-profit purposes.  Commercial use          *
 * permitted only by explicit agreement with Jim Kent (jim_kent@pacbell.net) *
 *****************************************************************************/
#ifndef MADBREP_H
#define MADBREP_H

/* maDbRep.h was originally generated by the autoSql program, which also 
 * generated maDbRep.c and maDbRep.sql.  This header links the database and the RAM 
 * representation of objects. */

struct mrnaAli
/* An mRNA/genomic alignment */
    {
    struct mrnaAli *next;  /* Next in singly linked list. */
    unsigned id;	/* Unique ID */
    signed char readDir;	/* Read direction of mRNA +1 or -1 */
    signed char orientation;	/* Orientation relative to first BAC */
    unsigned char hasIntrons;	/* True if alignment has introns */
    unsigned char isEst;	/* True if an EST. */
    int score;	/* Score in something like log-odds form */
    char qAcc[13];	/* GenBank Accession for mRNA sequence */
    unsigned qId;	/* Database ID of mRNA sequence */
    unsigned qTotalSize;	/* Total bases (not just aligned) in mRNA */
    unsigned qStart;	/* Start in mRNA sequence */
    unsigned qEnd;	/* End in mRNA sequence */
    unsigned tStartBac;	/* ID of first genomic BAC in alignment */
    unsigned tStartPos;	/* Start position within first BAC */
    unsigned tEndBac;	/* ID of last genomic BAC in alignment */
    unsigned tEndPos;	/* End position within last BAC */
    unsigned blockCount;	/* Number of aligned blocks */
    unsigned *blockSizes;	/* Size of each block */
    unsigned *qBlockStarts;	/* Start of each block in mRNA */
    unsigned *tBlockBacs;	/* BAC each block starts in */
    unsigned *tBlockStarts;	/* Position within BAC of each block start */
    unsigned short *startGoods;	/* Number of perfect bases at start of block */
    unsigned short *endGoods;	/* Number of perfect bases at end of block */
    };

struct mrnaAli *mrnaAliLoad(char **row);
/* Load a mrnaAli from row fetched with select * from mrnaAli
 * from database.  Dispose of this with mrnaAliFree(). */

void mrnaAliFree(struct mrnaAli **pEl);
/* Free a single dynamically allocated mrnaAli such as created
 * with mrnaAliLoad(). */

void mrnaAliFreeList(struct mrnaAli **pList);
/* Free a list of dynamically allocated mrnaAli's */

void mrnaAliOutput(struct mrnaAli *el, FILE *f, char sep, char lastSep);
/* Print out mrnaAli.  Separate fields with sep. Follow last field with lastSep. */

#define mrnaAliTabOut(el,f) mrnaAliOutput(el,f,'\t','\n');
/* Print out mrnaAli as a line in a tab-separated file. */

#define mrnaAliCommaOut(el,f) mrnaAliOutput(el,f,',',',');
/* Print out mrnaAli as a comma separated list including final comma. */

#endif /* MADBREP_H */
