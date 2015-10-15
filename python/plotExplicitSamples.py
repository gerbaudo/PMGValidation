#!/bin/env python

# plot a comparison of the central/up/down variations

# davide.gerbaudo@gmail.com
# Oct 2015

import glob
import os
import utils

import rootUtils as ru
R = ru.importRoot()

def main():
    ""
    outdir = './'
    input_nom = glob.glob('out/batch/510066/hist-ttW_sysWgt-0*.root')
    input_up = glob.glob('out/batch/610066/hist-ttW_scalUp-0*.root')
    input_do = glob.glob('out/batch/710066/hist-ttW_scalDn-0*.root')
    merge_is_needed = False
    if merge_is_needed:
        input_nom = merge(input_nom)
        input_up  = merge(input_up)
        input_do  = merge(input_do)
    input_nom = 'out/batch/510066/hist-ttW_sysWgt-00.root'
    input_up  = 'out/batch/610066/hist-ttW_scalUp-00.root'
    input_do  = 'out/batch/710066/hist-ttW_scalDn-00.root'
    for inputfile in [input_nom, input_up, input_do]:
        print "using input %s"%inputfile

    cross_sections = {'nom':0.17556, 'up':0.17776, 'do':0.17894}
    normalization_numbers = dict([(k, get_number_of_events(f))
                                  for k,f in (('nom', input_nom),
                                             ('up', input_up),
                                             ('do', input_do))])
    luminosity = 1.0
    normalization_integrals = dict([(k, cross_sections[k]*luminosity/normalization_numbers[k]) for k in ['nom', 'up', 'do']])
    histogram_names = get_histogram_names(input_nom)
    exclude_histograms = ['EventLoop_EventCount']
    histogram_names = [h for h in histogram_names if h not in exclude_histograms]
    histogram_names = ['h_jetPt']
    print histogram_names

    file_nom = R.TFile.Open(input_nom)
    histograms_nom = dict((n, file_nom.Get(n)) for n in histogram_names)
    file_up = R.TFile.Open(input_up)
    histograms_up = dict((n, file_up.Get(n)) for n in histogram_names)
    file_do = R.TFile.Open(input_do)
    histograms_do = dict((n, file_do.Get(n)) for n in histogram_names)
    
    for histogram_name in histogram_names:
        h_nom = histograms_nom[histogram_name]
        h_up  = histograms_up [histogram_name]
        h_do  = histograms_do [histogram_name]
        h_nom.SetLineWidth(2*h_nom.GetLineWidth())
        h_up.SetLineColor(R.kBlue)
        h_do.SetLineColor(R.kRed)
        for h, n in [(h_nom, normalization_integrals['nom']),
                     (h_up, normalization_integrals['up']),
                     (h_do, normalization_integrals['do'])]:
            ru.normalizeTo(h, n)

        pad_master = h_nom
        can = R.TCanvas('c_ttV_syst_'+histogram_name, 'ttV explicit variations '+pad_master.GetTitle())
        botPad, topPad = ru.buildBotTopPads(can, squeezeMargins=False)
        # top
        can.cd()
        topPad.Draw()
        topPad.cd()
        topPad._po = [pad_master] # persistent objects
        pad_master.Draw('axis')
        leg = ru.topRightLegend(can, 0.225, 0.325)
        leg.SetBorderSize(0)
        topPad._po.append(leg)
        for h,l in [(h_nom, 'nom'), (h_up, 'up'), (h_do, 'do')]:
            h.Draw('same')
            leg.AddEntry(h, l, 'l')
            topPad._po.append(h)
        leg.Draw('same')
        topPad.Update()
        # bottom
        can.cd()
        botPad.Draw()
        botPad.cd()
        ratio_up = ru.buildRatioHistogram(h_up, h_nom)
        ratio_do = ru.buildRatioHistogram(h_do, h_nom)
        yMin, yMax = 0.0, 2.0
        ratioPadMaster = pad_master.Clone(pad_master.GetName()+'_ratio')
        ratioPadMaster.SetMinimum(yMin)
        ratioPadMaster.SetMaximum(yMax)
        ratioPadMaster.SetStats(0)
        ratioPadMaster.Draw('axis')
        x_lo, x_hi = ru.getXrange(ratioPadMaster)
        refLines = [ru.referenceLine(x_lo, x_hi, y, y) for y in [0.5, 1.0, 1.5]]
        for l in refLines : l.Draw()
        ratio_up.Draw('same')
        ratio_do.Draw('same')
        xA, yA = ratioPadMaster.GetXaxis(), ratioPadMaster.GetYaxis()
        textScaleUp = 0.75*1.0/botPad.GetHNDC()
        yA.SetNdivisions(-104)
        yA.SetTitle('ratio')
        yA.CenterTitle()
        yA.SetTitleOffset(yA.GetTitleOffset()/textScaleUp)
        xA.SetTitleSize(yA.GetTitleSize()) # was set to 0 for padmaster, restore it
        xA.SetLabelSize(yA.GetLabelSize())
        for a in [xA, yA] :
            a.SetLabelSize(a.GetLabelSize()*textScaleUp)
            a.SetTitleSize(a.GetTitleSize()*textScaleUp)
        botPad._graphical_objects = [ratio_up, ratio_do, ratioPadMaster] + refLines # avoid garbage collection
        botPad.Update()
        can.Update()
        can.SaveAs(outdir+'/'+can.GetName()+'.png')

    file_do.Close()
    file_up.Close()
    file_nom.Close()
    
def get_number_of_events(input_filename='', histogram_name='h_numEvents'):
    "read from file the number of events that have been processed"
    input_file = R.TFile.Open(input_filename)
    histo = input_file.Get(histogram_name)
    number_of_events = histo.GetEntries()
    input_file.Close()
    return number_of_events

def get_histogram_names(input_filename=''):
    "get a list of histograms from a file"
    input_file = R.TFile.Open(input_filename)
    def is_histogram_key(k):
        return any(k.ReadObj().ClassName().startswith(p) for p in ['TH1','TH2','TH3'])
    names = [k.GetName() for k in input_file.GetListOfKeys() if is_histogram_key(k)]
    input_file.Close()
    return names

def merge(input_files=[], output_filename=''):
    "hadd a list of input files; return name merged file"
    prefix = utils.commonPrefix(input_files)
    suffix = utils.commonSuffix(input_files)
    if not output_filename:
        assert prefix and suffix, "guessing merged filename: prefix %s suffix %s"%(prefix, suffix)
        output_filename = prefix+'merged.root'
    cmd = "hadd %s %s" % (output_filename, ' '.join(input_files))
    out = utils.getCommandOutput(cmd)
    print cmd
    return output_filename if out['returncode']==0 else None

if __name__=='__main__':
    main()

