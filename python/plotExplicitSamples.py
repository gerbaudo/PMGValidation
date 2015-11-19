#!/bin/env python

description="""
plot a comparison of the central/up/down variations
"""
epilog="""
Example:
 ./PMGValidation/python/plotExplicitSamples.py -p ttll -s sherpa 2>&1 | tee out/ttll_sherpa.log
"""
# davide.gerbaudo@gmail.com
# Oct 2015

import argparse
import glob
import logging as log
import os
import utils
from math import sqrt

import rootUtils as ru
R = ru.importRoot()
style = ru.getAtlasStyle()
style.SetOptTitle(1)

def main():
    ""

def main() :
    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arg = parser.add_argument
    add_arg('-o', '--output-dir', default="./")
    add_arg('-p', '--process', help='one physics process, eg. ttw')
    add_arg('-s', '--systematic', help='one of the systematic variations')
    add_arg('-v', '--verbose', action='store_true')
    add_arg('-d', '--debug', action='store_true')
    args = parser.parse_args()

    set_log(args.verbose, args.debug)
    outdir = args.output_dir
    process = args.process
    systematic = args.systematic

    available_processes = get_input_samples().keys()
    if process not in available_processes:
        raise StandardError("invalid process %s, should be one of %s"%(process, str(available_processes)))
    available_systematics = get_input_samples()[process].keys()
    if systematic not in available_systematics:
        raise StandardError("invalid systematic %s, should be one of %s"%(systematic, str(available_systematics)))

    file_label = process+'_sys_'+systematic
    plot_label = process+' sys. '+systematic

    normalize_to_unity = False # True
    luminosity = 1.0

    combiner = HistogramCombiner()

    combiner.build_samples(process=process, systematic=systematic)
    histogram_names = ['h_meff', 'h_jetN',
                       # 'h_electronPt', 'h_muonPt',
                       'h_jetFlavorMultiplicity',
                       'h_bjetN',
                       # 'h_meff_sr3b', 'h_jetN_sr3b',
                       # 'h_meff_sr1b', 'h_jetN_sr1b',
                       # 'h_meff_sr0b5j', 'h_jetN_sr0b5j',
                       # 'h_meff_sr0b3j', 'h_jetN_sr0b3j',
                       # 'h_meff_cr2bttV', 'h_jetN_cr2bttV',
                       ]

    combiner.compute_normalization_factors()
    output_pdf_name = outdir+'/'+file_label+'.pdf'
    c_summary = R.TCanvas('c_summary', 'plotExplicitSamples sampes summary ')
    combiner.print_sample_summary_to_pdf(c_summary, label="%s: nominal vs. %s systematic"%(process, systematic))
    c_summary.SaveAs(output_pdf_name+'(')


    for histogram_name in histogram_names:
        rebin = 'meff' in histogram_name # and '_sr' in histogram_name # non-inclusive histos: low stats
        rebin_factor = (2 if 'meff' in histogram_name else 2 if 'jetN' in histogram_name else 1) if rebin else 1
        histograms = combiner.get_histograms(histogram_name=histogram_name)
        h_nom = histograms['nominal']
        h_up  = histograms['up']
        h_dn  = histograms['down']
        if 'h_jetFlavorMultiplicity' in histogram_name:
            h_nom = emulate_btag_multiplicity_from_truth_flavor(h_nom, 'nom')
            h_up  = emulate_btag_multiplicity_from_truth_flavor(h_up, 'up')
            h_dn  = emulate_btag_multiplicity_from_truth_flavor(h_dn, 'dn')
        histos = [h_nom, h_up, h_dn]
        for h in set(histos): # set: avoid rebinning twice when up==down
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
        def integral_and_error(h):
            error = R.Double(0.0)
            integral = h.IntegralAndError(1, h.GetNbinsX()+1, error)
            return integral, error
        def ratio_and_error(ave=(1.0, 0.01), bve=(2.0, 0.001)):
            a, sa = ave
            b, sb = bve
            if a and b:
                r = a/b
                e = r * sqrt((sa/a)*(sa/a)+(sb/b)*(sb/b))
                return r, e
            else:
                return 0.0, 0.0
        print_normalization_summary = histogram_name.startswith('h_meff')
        if print_normalization_summary:
            nom_int = h_nom.Integral()
            up_int = h_up.Integral()
            dn_int = h_dn.Integral()
            nom_int, nom_err = integral_and_error(h_nom)
            up_int, up_err = integral_and_error(h_up)
            dn_int, dn_err = integral_and_error(h_dn)
            rup, rupe = ratio_and_error((up_int, up_err), (nom_int, nom_err))
            rdn, rdne = ratio_and_error((dn_int, dn_err), (nom_int, nom_err))
            # print ("normalization change: "
            #        +"{} up {:.1%} down {:.1%} (nom {:.1f}, up {:.1f}, do {:.1f})".format(h_nom.GetName(),
            #                                                                           1.0-up_int/nom_int if nom_int else 1.0,
            #                                                                           1.0-dn_int/nom_int if nom_int else 1.0,
            #                                                                           nom_int,
            #                                                                           up_int,
            #                                                                           dn_int))
            print ("normalization change: "
                   +"{} up {:.1%} +/- {:.1%} down {:.1%} +/- {:.1%} ".format(h_nom.GetName(), 1.0-rup, rupe, 1.0-rdn, rdne)
                   +"(integral: "
                   +"nom {:.2E}  +/- {:.2E}, up {:.2E} +/- {:.2E}, do {:.2E} +/- {:.2E})".format(nom_int, nom_err,
                                                                                                 up_int, up_err,
                                                                                                 dn_int, dn_err))

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

            # print ("shape change: "
            #        +"{} up {:.1%} down {:.1%} ".format(h_nom.GetName(),
            #                                            1.0-max_frac_variation_within10(h_up, h_nom),
            #                                            1.0-max_frac_variation_within10(h_dn, h_nom)))

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
    if not histo:
        print "missing %s from %s"%(histogram_name, input_filename)
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
    input_files = [f for f in input_files if f is not output_filename]
    cmd = "hadd %s %s" % (output_filename, ' '.join(input_files))
    out = utils.getCommandOutput(cmd)
    log.info(cmd)
    if out['returncode']!=0:
        log.info(out['stdout'])
        log.error(out['stderr'])
    return output_filename if out['returncode']==0 else None

def get_input_samples():
    """
    dict with the input samples (files+xsec).
    each process has nominal + systematics; each systematic has up and down.
    nominal, up, and down have one or more subprocess, each with a xsec and some input files
    """
    base = 'batch/2015-11-18/out/'
    base_nom = base
    ttw = {
        'nominal' : {
            'ttWnp0_sysWgt' : { 'input_files' : base_nom+'ttW_410066/hist-ttW_*.root', 'xsec' : 0.176560 },
            'ttWnp1_sysWgt' : { 'input_files' : base_nom+'ttW_410067/hist-ttW_*.root', 'xsec' : 0.140620 },
            'ttWnp2_sysWgt' : { 'input_files' : base_nom+'ttW_410068/hist-ttW_*.root', 'xsec' : 0.136800 },
            },
        'scale' : {
            'up' : {
                'ttWnp0_scalUp' : { 'input_files' : base+'ttW_610066/hist-ttW_*.root', 'xsec' : 0.1437 },
                'ttWnp1_scalUp' : { 'input_files' : base+'ttW_610067/hist-ttW_*.root', 'xsec' : 0.11086 },
                'ttWnp2_scalUp' : { 'input_files' : base+'ttW_610068/hist-ttW_*.root', 'xsec' : 0.099048 },
                },
            'down' : {
                'ttWnp0_scalDn' : { 'input_files' : base+'ttW_710066/hist-ttW_*.root', 'xsec' : 0.24284 },
                'ttWnp1_scalDn' : { 'input_files' : base+'ttW_710067/hist-ttW_*.root', 'xsec' : 0.20288 },
                'ttWnp2_scalDn' : { 'input_files' : base+'ttW_710068/hist-ttW_*.root', 'xsec' : 0.21626 },
                },
            },
        'alpsfact' : {
            'up' : {
                'ttWnp0_alpsUp' : { 'input_files' : base+'ttW_810066/hist-ttW_*.root', 'xsec' : 0.1838 },
                'ttWnp1_alpsUp' : { 'input_files' : base+'ttW_810067/hist-ttW_*.root', 'xsec' : 0.1446 },
                'ttWnp2_alpsUp' : { 'input_files' : base+'ttW_810068/hist-ttW_*.root', 'xsec' : 0.13922 },
                },
            'down' : {
                'ttWnp0_alpsDn' : { 'input_files' : base+'ttW_910066/hist-ttW_*.root', 'xsec' : 0.18134 },
                'ttWnp1_alpsDn' : { 'input_files' : base+'ttW_910067/hist-ttW_*.root', 'xsec' : 0.14484 },
                'ttWnp2_alpsDn' : { 'input_files' : base+'ttW_910068/hist-ttW_*.root', 'xsec' : 0.1379 },
                },
            },
        }
    base_wwjj = base
    wwjj = { # wwjj, with xsec from AMI
        'nominal' : {
            'wwjj_EW4_nom'      : { 'input_files' : base_wwjj+'WWjj_361069/*.root', 'xsec' : 0.043004 },
            'wwjj_EW6_nom'      : { 'input_files' : base_wwjj+'WWjj_361070/*.root', 'xsec' : 0.043004 },
            },
        'FSF' : {
            'up' : {
                'wwjj_EW4_FSFup'    : { 'input_files' : base_wwjj+'WWjj_361643/*.root', 'xsec' : 0.025199 },
                'wwjj_EW6_FSFup'    : { 'input_files' : base_wwjj+'WWjj_361651/*.root', 'xsec' : 0.042077 },
                },
            'down' : {
                'wwjj_EW4_FSFdown'  : { 'input_files' : base_wwjj+'WWjj_361658/*.root', 'xsec' : 0.027240 },
                'wwjj_EW6_FSFdown'  : { 'input_files' : base_wwjj+'WWjj_361650/*.root', 'xsec' : 0.044477 },
                },
            },
        'QSF' : {
            'up' : {
                'wwjj_EW4_QSFup'    : { 'input_files' : base_wwjj+'WWjj_361645/*.root', 'xsec' : 0.025422 },
                'wwjj_EW6_QSFup'    : { 'input_files' : base_wwjj+'WWjj_361653/*.root', 'xsec' : 0.043590 },
            },
            'down' : {
                'wwjj_EW4_QSFdown'  : { 'input_files' : base_wwjj+'WWjj_361644/*.root', 'xsec' : 0.026935 },
                'wwjj_EW6_QSFdown'  : { 'input_files' : base_wwjj+'WWjj_361652/*.root', 'xsec' : 0.043747 },
                },
            },
        'RSF' : {
            'up' : {
                'wwjj_EW4_RSFup'    : { 'input_files' : base_wwjj+'WWjj_361647/*.root', 'xsec' : 0.021188 },
                'wwjj_EW6_RSFup'    : { 'input_files' : base_wwjj+'WWjj_361655/*.root', 'xsec' : 0.043495 },
                },
            'down' : {
                'wwjj_EW4_RSFdown'  : { 'input_files' : base_wwjj+'WWjj_361646/*.root', 'xsec' : 0.033690 },
                'wwjj_EW6_RSFdown'  : { 'input_files' : base_wwjj+'WWjj_361654/*.root', 'xsec' : 0.043010 },
                },
            },
        'CKKW' : {
            'up' : {
            'wwjj_EW6_CKKWup'   : { 'input_files' : base_wwjj+'WWjj_361649/*.root', 'xsec' : 0.042895 },
            'wwjj_EW4_CKKWup'   : { 'input_files' : base_wwjj+'WWjj_361657/*.root', 'xsec' : 0.024757 },
            },
            'down' : {
                'wwjj_EW6_CKKWdown' : { 'input_files' : base_wwjj+'WWjj_361648/*.root', 'xsec' : 0.043657 },
                'wwjj_EW4_CKKWdown' : { 'input_files' : base_wwjj+'WWjj_361656/*.root', 'xsec' : 0.026241 },
                },
            },
        }
    base_ttll = base
    ttll = {
        'nominal' : { # official samples, xsec from AMI
            'ttee_Np0'     : { 'input_files' : base_ttll+'ttll_410111/*.root', 'xsec' : 0.0088155 },
            'ttee_Np1'     : { 'input_files' : base_ttll+'ttll_410112/*.root', 'xsec' : 0.0143800 },
            'ttmumu_Np0'   : { 'input_files' : base_ttll+'ttll_410113/*.root', 'xsec' : 0.0088422 },
            'ttmumu_Np1'   : { 'input_files' : base_ttll+'ttll_410114/*.root', 'xsec' : 0.0143750 },
            'tttautau_Np0' : { 'input_files' : base_ttll+'ttll_410115/*.root', 'xsec' : 0.0090148 },
            'tttautau_Np1' : { 'input_files' : base_ttll+'ttll_410116/*.root', 'xsec' : 0.0146360 },
            },
        'sherpa' : { # from Rohin, xsec from https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/TtbarBoson
            'up' : {
                'ttll_6'       : { 'input_files' : base_ttll+'ttll_6/*.root', 'xsec' : 0.0975300 },
                },
            }
        }
    ttll['sherpa']['down'] = ttll['sherpa']['up']
    return {'ttw':ttw, 'ttll':ttll, 'wwjj':wwjj}

def set_log(verbose, debug):
    if verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
    elif debug:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")
    # log.info("This should be verbose.")
    # log.warning("This is a warning.")
    # log.error("This is an error.")

class HistogramCombiner:
    """
    Combine histograms from different sub-processes with different cross sections
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
            self.already_scaled = []
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
            if name not in self.already_scaled:
                entries  = h.GetEntries()
                lumi = 1.0
                filter_eff = 1.0 # josh says there's no filter applied
                k_factor = 1.0 # none for now
                sumw = self.sumw_of_processed_events # use the sumw of generated/processed events, not the accepted ones
                scale = (lumi * self.xsec * filter_eff * k_factor / sumw) if sumw else 1.0
                msg = "scaled %s: was %.4E"%(self.name+'_'+name, h.Integral())
                h.Scale(scale)
                log.debug("%s : scaling by %.3E"
                          " (lumi %.1E,  xsec %.3E, filter_eff %.2E, k_factor %.2E, sumw %.2E)"%
                          (self.name+'_'+name, scale,
                           lumi,  self.xsec,  filter_eff, k_factor, sumw))
                msg += " now %.4E"%h.Integral()
                log.debug(msg)
                self.already_scaled.append(name)
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
        self.normalize_to_inclusive = False

    def build_samples(self, process='ttw', systematic='sherpa'):
        Sample = HistogramCombiner.Sample
        samples_nom = get_input_samples()[process]['nominal']
        samples_up = get_input_samples()[process][systematic]['up']
        samples_dn = get_input_samples()[process][systematic]['down']
        self.groups['nominal'] = [Sample(name=k, input_files_wildcard=e['input_files'], xsec=e['xsec'])
                                  for k, e in samples_nom.iteritems()]
        self.groups['up'] = [Sample(name=k, input_files_wildcard=e['input_files'], xsec=e['xsec'])
                             for k, e in samples_up.iteritems()]
        self.groups['down'] = [Sample(name=k, input_files_wildcard=e['input_files'], xsec=e['xsec'])
                               for k, e in samples_dn.iteritems()]

    def get_histograms(self, histogram_name='', groups=[]):
        "provide, for each group, a histogram from the sum of the samples in the group"
        groups = groups if groups else self.groups.keys()
        tot_histograms = {}
        for group in groups:
            samples = self.groups[group]
            histograms = [s.get_histogram(histogram_name) for s in samples]
            if not histograms:
                raise StandardError("missing %s from %s"%(histogram_name, str(groups)))
            h_tot = histograms[0].Clone(histograms[0].GetName()+'_tot')
            for h in histograms[1:]:
                h_tot.Add(h)
            tot_histograms[group] = h_tot
            if self.normalize_to_unity:
                integral = h_tot.Integral()
                h_tot.Scale(1.0/integral if integral else 1.0)
            elif self.normalize_to_inclusive:
                h_tot.Scale(self.inclusive_normalization_scale[group])
        return tot_histograms

    def print_sample_summary_to_pdf(self, canvas, label=''):
        canvas.cd()
        text = R.TText()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.375*text.GetTextSize())
        lines = []
        if label:
            lines.append(label)
        for group in ['nominal', 'up', 'down']:
            samples = self.groups[group]
            lines.append(group)
            for s in samples:
                lines.append(s.summary())
        nLinesMax = 10
        [text.DrawTextNDC(0.02, 0.98 - 0.4*(iLine+0.5)/nLinesMax, line)
         for iLine,line in enumerate(lines) ]
        return text

    def compute_normalization_factors(self, histogram_name='h_meff'):
        """for each group, compute the normalizazion factor from an
        inclusive histogram. This can then be used to normalize the
        selection-specific histograms"""
        tot_histograms = self.get_histograms(histogram_name)
        self.inclusive_normalization_scale = {}
        # to compute these factors we want nominal, inclusive histos normalized to xsec
        self.normalize_to_unity = False
        self.normalize_to_inclusive = False
        for group, normalization_histogram in tot_histograms.iteritems():
            integral = normalization_histogram.Integral()
            scale_factor = 1.0/integral if integral else 1.0
            self.inclusive_normalization_scale[group] = scale_factor
            log.info("normalization factor for %s : %.3E"%(group, scale_factor))
        self.normalize_to_inclusive = True

def emulate_btag_multiplicity_from_truth_flavor(h_multiplicity_vs_flavor=None, sys=''):
    """
    Take the multiplicity vs. PartonTruthLabelID histogram from
    TruthReader.cxx and emulate the btag multiplicity.

    Multiply the number of truth jets with each flavor by the expected
    btag efficiency, and add them up to get an overall emulated b-tag
    multiplicity.
    """
    parameters = [{'label':x[0], 'pdg':x[1], 'btag_eff':x[2]}
                  for x in [('d',      1, 1/440.), # values from Ximo
                            ('u',      2, 1/440.),
                            ('s',      3, 1/440.),
                            ('c',      4, 1/8.),
                            ('b',      5, 0.70),
                            ('tau',   15, 1/26.),
                            ('t',      6, 0.0), # \todo not sure we need them: can they be assoc with a truth jet? check this
                            ('e',     11, 0.0),
                            ('nue',   12, 0.0),
                            ('mu',    13, 0.0),
                            ('numu',  14, 0.0),
                            ('nutau', 16, 0.0),
                            ('glu',   21, 0.0),
                            ('gam',   22, 0.0),
                            ]]
    h_m_vf_f = h_multiplicity_vs_flavor
    h_eff = h_m_vf_f.Clone(h_m_vf_f.GetName()+'_btag_eff_'+sys)
    h_eff.Reset()
    for flavor in range(1, 1+h_eff.GetXaxis().GetNbins()):
        default_btag_eff = 0.0
        btag_eff = next((x['btag_eff'] for x in parameters if x['pdg']==flavor), default_btag_eff)
        for multiplicity in range(1, 1+h_eff.GetYaxis().GetNbins()):
            h_eff.SetBinContent(flavor, multiplicity, btag_eff)
    h_eff.Multiply(h_m_vf_f)
    h_btag_multiplicity = h_eff.ProjectionY(h_eff.GetName()+'_btag_emulated_multiplicity')
    return h_btag_multiplicity

if __name__=='__main__':
    main()

