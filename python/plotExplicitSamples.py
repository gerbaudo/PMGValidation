#!/bin/env python

# plot a comparison of the central/up/down variations

# davide.gerbaudo@gmail.com
# Oct 2015

import glob
import logging as log
import os
import utils

import rootUtils as ru
R = ru.importRoot()
style = ru.getAtlasStyle()

def main():
    ""
    set_log()
    outdir = './'
    plot_label = 'ttW scale sys'
    normalize_to_unity = False # True
    luminosity = 1.0

    combiner = HistogramCombiner()
    combiner.build_samples(group='ttW_sysWgt', selected_samples=['ttWnp0_sysWgt', 'ttWnp1_sysWgt', 'ttWnp2_sysWgt'])
    # combiner.build_samples(group='ttW_scalUp', selected_samples=['ttWnp0_scalUp', 'ttWnp1_scalUp', 'ttWnp2_scalUp'])
    # combiner.build_samples(group='ttW_scalDn', selected_samples=['ttWnp0_scalDn', 'ttWnp1_scalDn', 'ttWnp2_scalDn'])
    combiner.build_samples(group='ttW_scalUp', selected_samples=['ttWnp0_scalUp', 'ttWnp1_scalUp', 'ttWnp2_scalUp'])
    combiner.build_samples(group='ttW_scalDn', selected_samples=['ttWnp0_scalDn', 'ttWnp1_scalDn', 'ttWnp2_scalDn'])
    combiner.normalize_to_unity = normalize_to_unity

    # histogram_names = get_histogram_names(input_nom) # todo : get histonames from first file
    # exclude_histograms = ['EventLoop_EventCount']
    # histogram_names = [h for h in histogram_names if h not in exclude_histograms]
    histogram_names = ['h_meff']

    for histogram_name in histogram_names:
        print histogram_name
        histograms = combiner.get_histograms(histogram_name=histogram_name)
        h_nom = histograms['ttW_sysWgt']
        h_up  = histograms['ttW_scalUp']
        h_dn  = histograms['ttW_scalDn']
        histos = [h_nom, h_up, h_dn]
        h_nom.SetLineWidth(2*h_nom.GetLineWidth())
        h_up.SetLineColor(R.kBlue)
        h_dn.SetLineColor(R.kRed)

        pad_master = h_nom
        pad_master.SetMaximum(1.1*max([h.GetMaximum() for h in histos]))
        pad_master.SetMinimum(1.0*min([0.0]+[h.GetMinimum() for h in histos]))
        pad_master.SetStats(0)
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
        leg.SetHeader(plot_label+"(lumi %.1f)"%luminosity)
        topPad._po.append(leg)
        def format_legend_label(h, l):
            return "{0}: {1:.2E} ({2:.0f})".format(l, h.Integral(), h.GetEntries())
        for h,l in [(h_nom, 'nom'), (h_up, 'up'), (h_dn, 'dn')]:
            h.Draw('hist same')
            leg.AddEntry(h, format_legend_label(h, l), 'l')
            topPad._po.append(h)
        leg.Draw('same')
        topPad.Update()
        # bottom
        can.cd()
        botPad.Draw()
        botPad.cd()
        ratio_up = ru.buildRatioHistogram(h_up, h_nom)
        ratio_dn = ru.buildRatioHistogram(h_dn, h_nom)
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
        ratio_dn.Draw('same')
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
        botPad._graphical_objects = [ratio_up, ratio_dn, ratioPadMaster] + refLines # avoid garbage collection
        botPad.Update()
        can.Update()
        can.SaveAs(outdir+'/'+can.GetName()+'.png')

def get_number_of_events(input_filename='', histogram_name='h_numEvents'):
    "read from file the number of events that have been processed"
    input_file = R.TFile.Open(input_filename)
    histo = input_file.Get(histogram_name)
    number_of_events = histo.GetEntries()
    input_file.Close()
    log.info("number_of_events: %d from %s"%(number_of_events, input_filename))
    return number_of_events

def get_histogram_names(input_filename=''):
    "get a list of histograms from a file"
    input_file = R.TFile.Open(input_filename)
    def is_histogram_key(k):
        return any(k.ReadObj().ClassName().startswith(p) for p in ['TH1','TH2','TH3'])
    names = [k.GetName() for k in input_file.GetListOfKeys() if is_histogram_key(k)]
    input_file.Close()
    return names

def guess_merged_filename(input_files=[]):
    prefix = utils.commonPrefix(input_files)
    suffix = utils.commonSuffix(input_files)
    assert prefix and suffix, "guessing merged filename: prefix '%s' suffix '%s' from %s"%(prefix, suffix, str(input_files))
    output_filename = prefix+'merged.root'
    return output_filename

def merge_if_needed(input_files=[]):
    "given files, merge if there's anything new"
    output_filename = guess_merged_filename(input_files)
    # note to self: sometimes the output file can be in the input list...skip it
    newest_input_file = max([f for f in input_files if f is not output_filename], key=os.path.getctime)
    do_merge = not os.path.exists(output_filename) or os.path.getctime(output_filename)<os.path.getctime(newest_input_file)
    output_filename = merge(input_files, output_filename) if do_merge else output_filename
    return output_filename

def merge(input_files=[], output_filename=''):
    "hadd a list of input files; return name merged file"
    cmd = "hadd %s %s" % (output_filename, ' '.join(input_files))
    out = utils.getCommandOutput(cmd)
    log.info(cmd)
    return output_filename if out['returncode']==0 else None

def get_input_samples():
    "xsecs from Josh"
    return {
        # ttW nominal
        'ttWnp0_sysWgt' : {
            'input_files' : 'out/batch/510066/hist-ttW_sysWgt-0*.root',
            'xsec' : 0.17556
            },
        'ttWnp1_sysWgt' : {
            'input_files' : 'out/batch/510067/hist-ttW_sysWgt-0*.root',
            'xsec' : 0.14134
            },
        'ttWnp2_sysWgt' : {
            'input_files' : 'out/batch/510068/hist-ttW_sysWgt-0*.root',
            'xsec' : 0.13792
            },
        # ttW scalUp
        'ttWnp0_scalUp' : {
            'input_files' : 'out/batch/610066/hist-ttW_scalUp-0*.root',
            'xsec' : 0.17776
            },
        'ttWnp1_scalUp' : {
            'input_files' : 'out/batch/610067/hist-ttW_scalUp-0*.root',
            'xsec' : 0.14182
            },
        'ttWnp2_scalUp' : {
            'input_files' : 'out/batch/610068/hist-ttW_scalUp-0*.root',
            'xsec' : 0.13596
            },
        # ttW scalDn
        'ttWnp0_scalDn' : {
            'input_files' : 'out/batch/710066/hist-ttW_scalDn-0*.root',
            'xsec' : 0.17894
            },
        'ttWnp1_scalDn' : {
            'input_files' : 'out/batch/710067/hist-ttW_scalDn-0*.root',
            'xsec' : 0.14156
            },
        'ttWnp2_scalDn' : {
            'input_files' : 'out/batch/710068/hist-ttW_scalDn-0*.root',
            'xsec' : 0.13726
            },
        # ttW alpsUp
        'ttWnp0_alpsUp' : {
            'input_files' : 'out/batch/810066/hist-ttW_alpsUp-0*.root',
            'xsec' : 0.17490
            },
        'ttWnp1_alpsUp' : {
            'input_files' : 'out/batch/810067/hist-ttW_alpsUp-0*.root',
            'xsec' : 0.14096
            },
        'ttWnp2_alpsUp' : {
            'input_files' : 'out/batch/810068/hist-ttW_alpsUp-0*.root',
            'xsec' : 0.13686
            },
        # ttW alpsDn
        'ttWnp0_alpsDn' : {
            'input_files' : 'out/batch/910066/hist-ttW_alpsDn-0*.root',
            'xsec' : 0.17532
            },
        'ttWnp1_alpsDn' : {
            'input_files' : 'out/batch/910067/hist-ttW_alpsDn-0*.root',
            'xsec' : 0.14216
            },
        'ttWnp2_alpsDn' : {
            'input_files' : 'out/batch/910068/hist-ttW_alpsDn-0*.root',
            'xsec' : 0.13632
            },
        }

def set_log():
    verbose = True
    if verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")
    # log.info("This should be verbose.")
    # log.warning("This is a warning.")
    # log.error("This is an error.")

class HistogramCombiner:
    """
    Combine histograms from different processes with different cross sections
    Avoid opening files multiple times.
    """
    class Sample:
        def __init__(self, name, input_files_wildcard, xsec):
            self.name = name
            self.xsec = xsec
            input_files = glob.glob(input_files_wildcard)
            if not input_files or len(input_files)==1:
                log.warning("no files matching '%s' : %s"%(input_files_wildcard, str(input_files)))
            self.input_file = merge_if_needed(input_files)
            self.number_of_events = get_number_of_events(self.input_file)
            self.input_file = R.TFile.Open(self.input_file)
            log.info("using input %s"%self.input_file.GetName())

        def get_histogram(self, name=''):
            h = self.input_file.Get(name)
            normalization = self.xsec/self.number_of_events
            h.Scale(normalization)
            return h

    def __init__(self):
        self.groups = {} # where the samples will be stored
        self.normalize_to_unity = False

    def build_samples(self, selected_samples=[], group=''):
        samples = get_input_samples()
        Sample = HistogramCombiner.Sample
        self.groups[group] = [Sample(name=k, input_files_wildcard=e['input_files'], xsec=e['xsec'])
                             for k, e in samples.iteritems() if k in selected_samples]
    def get_histograms(self, histogram_name='', groups=[]):
        "provide, for each group, a histogram from the sum of the samples in the group"
        groups = groups if groups else self.groups.keys()
        tot_histograms = {}
        for group in groups:
            samples = self.groups[group]
            histograms = [s.get_histogram(histogram_name) for s in samples]
            h_tot = histograms[0]
            for h in histograms[1:]:
                h_tot.Add(h)
            tot_histograms[group] = h_tot
            if self.normalize_to_unity:
                integral = h_tot.Integral()
                h_tot.Scale(1.0/integral if integral else 1.0)
        return tot_histograms

if __name__=='__main__':
    main()

