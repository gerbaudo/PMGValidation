# PMGValidation


This Package was built with the help of the tutorial:
https://twiki.cern.ch/twiki/bin/view/AtlasComputing/SoftwareTutorialxAODAnalysisInROOT

It actually works on `AnalysisBase 2.3.11`:
```
rcSetup Base,2.3.11
```
It didn't with newer version but I'm sure that it should also work.

To compile:
``
rc find_packages
rc compile
``

The package contains one class called `TruthReader`.
This is the code which read TRUTH1 xAOD and built histograms from it.
The output will be a .root file containing all the histograms
Then, one can treat this root file, to set his own style and draw it in whatever format.
The package Atlas* class are there to build histograms with Atlas Style.

The `util/` folder contains all the code to execute.
`TruthPlot` use the call `TruthReader` to build a folder which contains the output histograms
`MergeHisto` is my own code which plot both histogram in one single histogram with a ratio plot.
But I would suggest that you build your own code for that.

In the `script/` folder, you can find a example launch.sh which create a validation pdf file with two samples

To use `TruthPlot`, do :
```
TruthPlot InputFolder/ Truth1_Input_xAOD.root OutputFolder/
```

When running this code, Make sure that the `OutputFolder` doesn't already exist !!!!
It won't work otherwise
Then you can find your .root output file in the `OutputFoder/`

To plot histograms from 2 samples in one pdf file, do :

```
MergeHisto Sample1.root Sample2.root Output.pdf
```

Any questions : simon.paul.berlendis@cern.ch

