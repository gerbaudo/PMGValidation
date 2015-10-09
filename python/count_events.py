#!/bin/env python

# Just count the entries from a list of files or filelist
#
# davide.gerbaudo@gmail.com
# Oct 2015

import sys
import warnings

def main():
    import ROOT as R
    R.gROOT.SetBatch(1)
    R.PyConfig.IgnoreCommandLineOptions = True # don't let root steal your cmd-line options
    warnings.filterwarnings( action='ignore', category=RuntimeWarning, message='.*no dictionary for.*' )
    treename = 'CollectionTree'
    
    txt_inputs = [f for f in sys.argv if '.txt' in f]
    root_inputs = [f for f in sys.argv if '.root' in f]
    file_names = [root_inputs]
    for txt_input in txt_inputs:
        file_names += files_from_txt(txt_input)
    file_names = [f for f in file_names if f]
 
    chain = R.TChain(treename)
    for file_name in file_names:
        chain.Add(file_name)
    print chain.GetEntries()


def files_from_txt(txt_filename):
    filenames = []
    with open(txt_filename) as input_file:
        filenames = [l.strip() for l in input_file.readlines() if '.root' in l]
    return filenames

if __name__=='__main__':
    main()
