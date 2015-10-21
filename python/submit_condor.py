#!/bin/env python

# submit PMGValidation/util/TruthPlot.cxx jobs to the condor queue.
#
# based on susynt/susynt-submit/python/submit_condor.py
#
# Initial setup
#  : source ~/dotfiles/bash_profile_gpatlas
#  : lsetup "rcsetup Base,2.3.11"
#  : git clone git@github.com:gerbaudo/PMGValidation.git
#  : rc find_packages
#  : rc compile
#  : cd PMGValidation/
#
#  Subsequent shells:
#  : lsetup fax
#  : lsetup "rcsetup"
#
# davide.gerbaudo@gmail.com
#  October 2015

import logging as log
import subprocess
import sys
import errno
import os
import glob
from argparse import ArgumentParser
import re

fax_is_checked = False

def main() :
    parser = ArgumentParser(description="NtMaker Condor Submission")
    add_arg = parser.add_argument
    add_arg('-i', '--input-files', required=True, nargs='*', help='input txt files containing the input datasets')
    add_arg('-o', '--output-dir', default="./batch", help='Directory to store the output.')
    # add_arg('-n', '--nEvents', default="-1", help="Set the number of events to process")
    add_arg('-p', '--pattern', default='.*', help='grep pattern to select datasets')
    add_arg('-S', '--submit', action='store_true', help='actually submit jobs')
    add_arg('-v', '--verbose', action='store_true')
    add_arg('--run-site', default='1', help='Set cluster option [1:brick-only, 2:brick+local, 3:brick+local+SDSC, 4:brick+local+SDSC+UCs] (default: 1)')
    args = parser.parse_args()

    set_log(args.verbose)
    input_files = args.input_files
    # nEvents     = float(args.nEvents)
    pattern     = args.pattern
    run_site    = args.run_site
    site_option   = ("brick+local+SDSC+UC" if run_site=='4' else
                     "brick+local+SDSC" if run_site=='3' else
                     "brick+local" if run_site=='2' else
                     "brick-only")
    submit = args.submit
    log.info("options:\ninput file: {}\npattern: {}\nsite option: {}".format(input_files, pattern, site_option))
    for iInput_file, input_file in enumerate(input_files) :
        iSample = 0
        file_label = without_extension(input_file)
        with open(input_file) as lines :
            samples = [l.strip() for l in lines if is_interesting_line(line=l, regexp=pattern)]
            check_if_scoped(samples)
            for scoped_sample in samples :
                sample = drop_scope(scoped_sample)
                sample_label = file_label+'_'+dsid_from_samplename(sample)
                if not re.search(pattern, sample):
                    continue
                log.info("\t[%s] :  %s"%(sample_label, sample))
                dest_dir = args.output_dir.rstrip('/')
                log_dir = dest_dir+'/log/'
                scr_dir = dest_dir+'/script/'
                out_dir = dest_dir+'/out/'+sample_label # store output separately for each sample
                for d in [log_dir, out_dir, scr_dir]:
                    mkdir_p(d)
                # now submit one job per file
                fax_files = get_FAX_files(sample)
                for fax_file in fax_files :
                    log.info("\tfile: %s"%fax_file)
                    sub_name = "%s_%03d_%03d"%(sample_label, iInput_file, iSample)
                    condor_name = sub_name+'.condor'
                    input_container = sample
                    # if 'user.gerbaudo.6648972.EXT0._000005.DAOD_TRUTH1.pool.root' not in fax_file:
                    #     continue
                    condor_script = build_condor_script(site_option=site_option, samplename=sub_name, abs_dest_dir=os.path.abspath(out_dir), script_dir=scr_dir)
                    condor_execut = build_condor_executable(samplename=sub_name, script_dir=scr_dir, abs_dest_dir=os.path.abspath(out_dir))

                    base_dir = os.environ.get('ROOTCOREBIN').rstrip('/').replace('RootCoreBin', '')
                    script_arguments = ' '+base_dir+' '+fax_file+' '+sub_name+' '+out_dir
                    log_cmd = ' -append "log    = %s/%s.log" '%(os.path.abspath(log_dir), sub_name)
                    err_cmd = ' -append "error  = %s/%s.out" '%(os.path.abspath(log_dir), sub_name)
                    out_cmd = ' -append "output = %s/%s.err" '%(os.path.abspath(log_dir), sub_name)
                    # see email 'Questions from condor newbie' on 2015-10-13
                    run_cmd = 'ARGS="'+script_arguments+'" condor_submit '+condor_script+' '+log_cmd+' '+err_cmd+' '+out_cmd

                    log.info(run_cmd)
                    if submit:
                        subprocess.call(run_cmd, shell=True)
                    iSample += 1


def build_condor_script(site_option='', samplename='', abs_dest_dir='', script_dir='batch/script') :
    """Provide a condor submission script

    Note to self: the 'transfer_output_remaps' is not working (the
    output is copied to the submission dir instead of
    'abs_dest_dir'). Do a 'cp' within the 'condor.sh' script instead.
    """
    condor_submit_name = script_dir+'/'+samplename+'.condor'
    condor_exe_name = script_dir+'/'+samplename+'.sh'
    site_local = 'local' in site_option
    site_sdsc = 'SDSC' in site_option
    site_uc = 'UC' in site_option

    template = """
universe = vanilla
+local=true
+site_local=%(site_local)s
+sdsc=%(site_sdsc)s
+uc=%(site_uc)s
executable = %(condor_exe_name)s
arguments = $ENV(ARGS)
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_output_files = out/hist-%(samplename)s.root
transfer_output_remaps = "out/hist-%(samplename)s.root = %(dest_dir)s/hist-%(samplename)s.root"
use_x509userproxy = True
notification = Never
queue
"""
    def format_bool(v):
        return str(bool(v)).lower()
    file_ = open(condor_submit_name, 'w')
    file_.write(template % {'site_local':format_bool(site_local),
                            'site_sdsc':format_bool(site_sdsc),
                            'site_uc':format_bool(site_uc),
                            'condor_exe_name':condor_exe_name,
                            'samplename':samplename,
                            'dest_dir':abs_dest_dir})
    file_.close()
    return condor_submit_name

def build_condor_executable(samplename='', script_dir='batch/script', abs_dest_dir='') :
    "If condor script is not available, write one"
    condor_exe_name = script_dir+'/'+samplename+'.sh'
    template = """#!/bin/bash

BASE_DIR=$1
INPUT_FILE=$2
SAMPLE=$3
OUTPUT_DIR=$4

# set -e # exit on error
# set -u # exit on undefined variable

echo "Using these options:"
echo "BASE_DIR         $BASE_DIR       "
echo "INPUT_FILE       $INPUT_FILE     "
echo "SAMPLE           $SAMPLE         "
echo "OUTPUT_DIR       $OUTPUT_DIR     "

local_filelist="filelist.txt"
local_outdir="out"
exe_options="--filelist ${local_filelist} --sample-name ${SAMPLE} -o ${local_outdir}"
exe="TruthPlot"

OUT_LOCAL_FILE="out/hist-${SAMPLE}.root"

WORK_DIR=$(pwd)
echo "Working in ${WORK_DIR}"
date

echo "Using the input file ${INPUT_FILE}"

cd ${BASE_DIR}
echo "Now in `pwd`"
echo "Setting up RootCore"
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh

lsetup fax
source RootCoreBin/local_setup.sh
echo "Using root `root-config --version` from `which root`"

echo Using `which ${exe}`
echo Starting `date`

cd ${WORK_DIR}

echo "${INPUT_FILE}" > "${local_filelist}"

${exe} ${exe_options}

echo Contents after processing:
ls -ltrh
ls -ltrh ${OUT_LOCAL_FILE}
md5sum ${OUT_LOCAL_FILE}
cp -p ${OUT_LOCAL_FILE} %(abs_dest_dir)s/$(basename ${OUT_LOCAL_FILE})

echo Finished `date`

"""
    file_ = open(condor_exe_name, 'w')
    file_.write(template%{'abs_dest_dir':abs_dest_dir})
    file_.close()
    return condor_exe_name

def get_FAX_files(input_dataset) :
    global fax_is_checked
    if not fax_is_checked :
        if os.environ.get('STORAGEPREFIX') == None :
            log.error("STORAGEPREFIX environment variable is empty.")
            log.error("You must call 'localSetupFAX' before running.")
            sys.exit()
        fax_is_checked = True

    out_files = []
    cmd = 'fax-get-gLFNs %s > tmp_glfns.txt'%input_dataset
    subprocess.call(cmd, shell=True)
    files = open("tmp_glfns.txt").readlines()
    for file in files :
        if not file : continue
        file = file.strip()
        out_files.append(file)
    cmd = "rm tmp_glfns.txt"
    subprocess.call(cmd, shell=True)
    return out_files


def check_if_scoped(input_lines) :
    """
    FAX prefers to have scoped datasets but not absolutely necessary, see
    https://twiki.cern.ch/twiki/bin/view/AtlasComputing/UsingFAXforEndUsersTutorial
    """
    n_warnings = 1
    for line in input_lines :
        if ':' not in line and n_warnings < 10 :
            log.warning("Providing input dataset without scope prefix: %s [%d/10]"%(line, n_warnings))
            n_warnings += 1

def drop_scope(sample):
    return sample.split(':')[1] if ':' in sample else sample

def is_interesting_line(line='', regexp='') :
    "interesting line: non-comment, non-empty, one name, matching selection"
    line = line.strip()
    tokens = line.split()
    return (len(line)>0 and not line.startswith('#') and len(tokens)==1 and re.search(regexp, line))

def without_extension(filename=''):
    filename = os.path.basename(filename).split('.')[0]
    return filename

def dsid_from_samplename(samplename=''):
    "expect dsid to be a 6-digit number between two dots"
    match = re.search('\.(?P<dsid>\d{6})\.', samplename)
    return match.group('dsid')

def set_log(verbose):
    if verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")
    # log.info("This should be verbose.")
    # log.warning("This is a warning.")
    # log.error("This is an error.")

def mkdir_p(path):
    "http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python"
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
#__________________________________
if __name__ == "__main__" :
    main()
