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
style.SetOptTitle(1)

def main():
    ""
    set_log()
    outdir = './'
    do_scale = True # False
    do_alps = not do_scale
    # file_label = 'ttWnp0_scale_sys'
    # plot_label = 'ttWnp0 scale sys'
    file_label = 'ttW_scale_sys' if do_scale else 'ttW_alps_sys'
    plot_label = 'ttW scale sys' if do_scale else 'ttW alps sys'
    normalize_to_unity = True # False
    luminosity = 1.0

    combiner = HistogramCombiner()
    combiner.build_samples(group='ttW_sysWgt', selected_samples=['ttWnp0_sysWgt', 'ttWnp1_sysWgt', 'ttWnp2_sysWgt'])
    if do_scale:
        combiner.build_samples(group='ttW_scalUp', selected_samples=['ttWnp0_scalUp', 'ttWnp1_scalUp', 'ttWnp2_scalUp'])
        combiner.build_samples(group='ttW_scalDn', selected_samples=['ttWnp0_scalDn', 'ttWnp1_scalDn', 'ttWnp2_scalDn'])
    else:
        combiner.build_samples(group='ttW_alpsUp', selected_samples=['ttWnp0_alpsUp', 'ttWnp1_alpsUp', 'ttWnp2_alpsUp'])
        combiner.build_samples(group='ttW_alpsDn', selected_samples=['ttWnp0_alpsDn', 'ttWnp1_alpsDn', 'ttWnp2_alpsDn'])
    # combiner.build_samples(group='ttW_sysWgt', selected_samples=['ttWnp0_sysWgt'                                  ])
    # combiner.build_samples(group='ttW_scalUp', selected_samples=['ttWnp0_scalUp'                                  ])
    # combiner.build_samples(group='ttW_scalDn', selected_samples=['ttWnp0_scalDn'                                  ])
    # combiner.build_samples(group='ttW_sysWgt', selected_samples=[                 'ttWnp1_sysWgt'                 ])
    # combiner.build_samples(group='ttW_scalUp', selected_samples=[                 'ttWnp1_scalUp'                 ])
    # combiner.build_samples(group='ttW_scalDn', selected_samples=[                 'ttWnp1_scalDn'                 ])
    # combiner.build_samples(group='ttW_sysWgt', selected_samples=[                                  'ttWnp2_sysWgt'])
    # combiner.build_samples(group='ttW_scalUp', selected_samples=[                                  'ttWnp2_scalUp'])
    # combiner.build_samples(group='ttW_scalDn', selected_samples=[                                  'ttWnp2_scalDn'])
    combiner.normalize_to_unity = normalize_to_unity

    # histogram_names = get_histogram_names(input_nom) # todo : get histonames from first file
    # exclude_histograms = ['EventLoop_EventCount']
    # histogram_names = [h for h in histogram_names if h not in exclude_histograms]
    histogram_names = ['h_meff', 'h_jetN',
                       'h_meff_sr3b', 'h_jetN_sr3b',
                       'h_meff_sr1b', 'h_jetN_sr1b',
                       'h_meff_sr0b5j', 'h_jetN_sr0b5j',
                       'h_meff_sr0b3j', 'h_jetN_sr0b3j',
                       'h_meff_cr2bttV', 'h_jetN_cr2bttV',
                       ]

    output_pdf_name = outdir+'/'+file_label+'.pdf'
    c_summary = R.TCanvas('c_summary', 'plotExplicitSamples sampes summary ')
    combiner.print_sample_summary_to_pdf(c_summary)
    c_summary.SaveAs(output_pdf_name+'(')

    for histogram_name in histogram_names:
        rebin = 'meff' in histogram_name and '_sr' in histogram_name # non-inclusive histos: low stats
        rebin = True
        rebin_factor = (25 if 'meff' in histogram_name else 2 if 'jetN' in histogram_name else 1) if rebin else 1
        histograms = combiner.get_histograms(histogram_name=histogram_name)
        h_nom = histograms['ttW_sysWgt']
        h_up  = histograms['ttW_scalUp' if do_scale else 'ttW_alpsUp']
        h_dn  = histograms['ttW_scalDn' if do_scale else 'ttW_alpsDn']
        histos = [h_nom, h_up, h_dn]
        for h in histos:
            h.Rebin(rebin_factor)
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
        ru.topRightLabel(topPad, pad_master.GetTitle(), xpos=0.5)

        leg = ru.topRightLegend(can, 0.225, 0.325)
        leg.SetBorderSize(0)
        leg.SetHeader(plot_label+ ("(norm=1)" if normalize_to_unity else "(lumi %.1f)"%luminosity))
        topPad._po.append(leg)
        def format_legend_label(h, l):
            return "{0}: {1:.2E} ({2:.0f})".format(l, h.Integral(), h.GetEntries())
        for h,l in [(h_nom, 'nom'), (h_up, 'up'), (h_dn, 'dn')]:
            h.Draw('hist same')
            leg.AddEntry(h, format_legend_label(h, l), 'l')
            topPad._po.append(h)
        leg.Draw('same')
        if True:
            nom_int = h_nom.Integral()
            up_int = h_up.Integral()
            dn_int = h_dn.Integral()
            print ("normalization change: "
                   +"{} up {:.1%} down {:.1%} (nom {:.1f}, up {:.1f}, do {:.1f})".format(h_nom.GetName(),
                                                                                      1.0-up_int/nom_int,
                                                                                      1.0-dn_int/nom_int,
                                                                                      nom_int,
                                                                                      up_int,
                                                                                      dn_int))
            def bc(h): return [h.GetBinContent(i) for i in range(1,1+h.GetNbinsX())]
            def max_frac_variation(h1, h2):
                "maximum bin-by-bin fractional variation; h1 is denominator, empty bins skipped"
                bc1 = bc(h1)
                bc2 = bc(h2)
                return max([abs(b2/b1) for b1, b2 in zip(bc1, bc2) if b1 and b2])
            def max_frac_variation_within10(h1, h2):
                """maximum bin-by-bin fractional variation; h1 is denominator.
                Bins with <0.1*peak are skipped"""
                bc1 = bc(h1)
                bc2 = bc(h2)
                m1 = max(bc1)
                m2 = max(bc2)
                return max([abs(b2/b1) for b1, b2 in zip(bc1, bc2) if b1>0.1*m1 and b2>0.1*m2])

            print ("shape change: "
                   +"{} up {:.1%} down {:.1%} ".format(h_nom.GetName(),
                                                       1.0-max_frac_variation_within10(h_up, h_nom),
                                                       1.0-max_frac_variation_within10(h_dn, h_nom)))

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
        first_histo = histogram_name is histogram_names[0]
        last_histo  = histogram_name is histogram_names[-1]
        can.SaveAs(outdir+'/'+can.GetName()+'.png')
        can.SaveAs(output_pdf_name+ (')' if last_histo else ''))


def get_n_and_sumw_of_processed_events(input_filename='', histogram_name='h_numEvents'):
    "read from file the number of events that have been processed, and their sumw"
    histogram_name = 'h_jetN'
    log.warning('fixme bug h_numEvents')
    input_file = R.TFile.Open(input_filename)
    if not input_file:
        raise IOError("missing %s"%input_filename)
    histo = input_file.Get(histogram_name)
    number_of_processed_events = histo.GetEntries()
    sumw_of_processed_events = histo.Integral()
    input_file.Close()
    log.debug("%s: N events %.1f. sumw %.1f)"%(input_filename, number_of_processed_events, sumw_of_processed_events))
    return number_of_processed_events, sumw_of_processed_events

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
    cmd = "hadd %s %s" % (output_filename, ' '.join(input_files))
    out = utils.getCommandOutput(cmd)
    log.info(cmd)
    return output_filename if out['returncode']==0 else None

def get_input_samples():
    "xsecs from Josh"
    base='out/batch_10k/' # lxplus:work/public/samesign_jets/ttVsystematics/make_plots
    base='batch/out/' # uclhc-1:ss3l/ttVsystematics/make_plots
    base_nom='batch/2015-11-03/out/' # uclhc-1 take2
    base='batch/2015-11-05/out/' # uclhc-1 take3 (new samples from Josh)
    return {
        # ttW nominal
        'ttWnp0_sysWgt' : {
            'input_files' : base_nom+'ttW_410066/hist-ttW_*.root',
            'xsec' : 0.176560
            },
        'ttWnp1_sysWgt' : {
            'input_files' : base_nom+'ttW_410067/hist-ttW_*.root',
            'xsec' : 0.140620
            },
        'ttWnp2_sysWgt' : {
            'input_files' : base_nom+'ttW_410068/hist-ttW_*.root',
            'xsec' : 0.136800
            },
        # ttW scalUp
        'ttWnp0_scalUp' : {
            'input_files' : base+'ttW_610066/hist-ttW_*.root',
            'xsec' : 0.1437
            },
        'ttWnp1_scalUp' : {
            'input_files' : base+'ttW_610067/hist-ttW_*.root',
            'xsec' : 0.11086
            },
        'ttWnp2_scalUp' : {
            'input_files' : base+'ttW_610068/hist-ttW_*.root',
            'xsec' : 0.099048
            },
        # ttW scalDn
        'ttWnp0_scalDn' : {
            'input_files' : base+'ttW_710066/hist-ttW_*.root',
            'xsec' : 0.24284
            },
        'ttWnp1_scalDn' : {
            'input_files' : base+'ttW_710067/hist-ttW_*.root',
            'xsec' : 0.20288
            },
        'ttWnp2_scalDn' : {
            'input_files' : base+'ttW_710068/hist-ttW_*.root',
            'xsec' : 0.21626
            },
        # ttW alpsUp
        'ttWnp0_alpsUp' : {
            'input_files' : base+'ttW_810066/hist-ttW_*.root',
            'xsec' : 0.1838
            },
        'ttWnp1_alpsUp' : {
            'input_files' : base+'ttW_810067/hist-ttW_*.root',
            'xsec' : 0.1446
            },
        'ttWnp2_alpsUp' : {
            'input_files' : base+'ttW_810068/hist-ttW_*.root',
            'xsec' : 0.13922
            },
        # ttW alpsDn
        'ttWnp0_alpsDn' : {
            'input_files' : base+'ttW_910066/hist-ttW_*.root',
            'xsec' : 0.18134
            },
        'ttWnp1_alpsDn' : {
            'input_files' : base+'ttW_910067/hist-ttW_*.root',
            'xsec' : 0.14484
            },
        'ttWnp2_alpsDn' : {
            'input_files' : base+'ttW_910068/hist-ttW_*.root',
            'xsec' : 0.1379
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
            self.input_files_wildcard = input_files_wildcard
            input_files = glob.glob(input_files_wildcard)
            if not input_files:
                log.warning("no files matching '%s' : %s"%(input_files_wildcard, str(input_files)))
            self.input_file = self.merge_if_needed(input_files)
            if not self.input_file:
                raise IOError("missing input file for %s  using %s"%(self.name, self.input_files_wildcard))
            self.number_of_processed_events, self.sumw_of_processed_events = get_n_and_sumw_of_processed_events(self.input_file)
            self.input_file = R.TFile.Open(self.input_file)
            log.info("using input %s"%self.input_file.GetName())
        def guess_merged_filename(self, input_files=[]):
            if not input_files:
                raise StandardError("no input files to be merged")
            uniq_input_dirs=list(set(os.path.dirname(f) for f in input_files))
            all_in_one_dir = len(uniq_input_dirs)==1
            if not all_in_one_dir:
                raise StandardError("files to be merged must be in the same dir: %s"%str(uniq_input_dirs))
            output_filename = os.path.join(uniq_input_dirs[0], 'merged.root')
            return output_filename
        def merge_if_needed(self, input_files=[]):
            "given files, merge if there's anything new"
            output_filename = self.guess_merged_filename(input_files)
            input_files = [f for f in input_files if f is not output_filename]
            # note to self: sometimes the output file can be in the input list...skip it
            newest_input_file = max([f for f in input_files if f is not output_filename], key=os.path.getctime)
            newest_after_output = os.path.exists(output_filename) and os.path.getctime(output_filename)<os.path.getctime(newest_input_file)
            if newest_after_output: os.remove(output_filename)
            do_merge = not os.path.exists(output_filename)
            output_filename = merge(input_files, output_filename) if do_merge else output_filename
            self.input_files = input_files
            return output_filename

        def get_histogram(self, name=''):
            h = self.input_file.Get(name)
            entries  = h.GetEntries()
            lumi = 1.0
            filter_eff = 1.0 # josh says there's no filter applied
            k_factor = 1.0 # none for now
            sumw = self.sumw_of_processed_events # use the sumw of generated/processed events, not the accepted ones
            scale = (lumi * self.xsec * filter_eff * k_factor / sumw) if sumw else 1.0
            h.Scale(scale)
            log.debug("%s : scaling by %.3E"
                     " (lumi %.1E,  xsec %.3E, filter_eff %.2E, k_factor %.2E, sumw %.2E)"%
                     (self.name, scale,
                      lumi,  self.xsec,  filter_eff, k_factor, sumw))
            return h
        def summary(self):
            "a one-line summary of this sample"
            sep = 5*' '
            return sep.join([self.name,
                             "%s (%d files)"%(self.input_files_wildcard, len(self.input_files)),
                             "xsec: %.3E"%self.xsec,
                             "nEvents: %.3E"%self.number_of_processed_events,
                             "sumW: %.3E"%self.sumw_of_processed_events])

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

    def print_sample_summary_to_pdf(self, canvas):
        canvas.cd()
        text = R.TText()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.375*text.GetTextSize())
        lines = []
        for group, samples in self.groups.items():
            lines.append(group)
            for s in samples:
                lines.append(s.summary())
        nLinesMax = 10
        [text.DrawTextNDC(0.02, 0.98 - 0.4*(iLine+0.5)/nLinesMax, line)
         for iLine,line in enumerate(lines) ]
        return text


if __name__=='__main__':
    main()

