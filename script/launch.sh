
# First Sample 
TruthPlot /data1/atlas/berlendis/Data/4top/ DAOD_TRUTH1.mc12_4top.pool.root mc12_4top

#Second Sample
TruthPlot /data1/atlas/berlendis/Data/4top/ DAOD_TRUTH1.mc15_4top_NNPDF.pool.root mc15_4top_NNPDF

#Compare the both histogram samples
MergeHisto mc12_4top/hist-DAOD_TRUTH1.mc12_4top.pool.root.root mc15_4top_NNPDF/hist-DAOD_TRUTH1.mc15_4top_NNPDF.pool.root.root ./4top_NNPDF_validation.pdf

