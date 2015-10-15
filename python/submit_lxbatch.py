#!/bin/env python

# given an eos filelist, submit jobs for each file
#
# davide.gerbaudo@gmail.com
# Oct 2015

# for each file you need to run something like
# TruthPlot -v -f  /tmp/gerbaudo/dummy_list.txt -s samplename -o out/foo -n 10 2>&1
# the output will be in out/foo/hist-samplename.root
# get base from ROOTCOREBIN/

import os, sys, time
from optparse import OptionParser
from count_events import files_from_txt

parser = OptionParser()
parser.add_option('-i', '--input-file', help='filelist on eos')
parser.add_option('-o', '--output-dir')
parser.add_option('-q', '--queue', default='8nm', help='see bqueues')
parser.add_option('-l', '--label', help='only used in jobname')
parser.add_option("-s", "--sample", help="sample name")
parser.add_option("-S", "--submit", action="store_true", default=False, help="Actually submit the jobs")

(options, args) = parser.parse_args()

if not options.input_file: parser.error('input file not given')
if not options.output_dir: parser.error('output dir not given')

thisScript = os.path.realpath(__file__)
packageDirectory = thisScript[:thisScript.find('PMGValidation/python/')]+'PMGValidation'
batchScript=packageDirectory+'/script/run_TruthPlot.sh'

output_dir = options.output_dir
if not os.path.isdir(output_dir):
    print 'making dir ',output_dir
    os.makedirs(output_dir)

files_to_process = files_from_txt(options.input_file)
jobIds = ["%04d"%i for i in range(len(files_to_process))]
output_dir = options.output_dir
queue = options.queue
rootcorebin = 'no-rootcorebin'
try:
    rootcorebin = os.environ['ROOTCOREBIN']
    parser.error("Please submit the jobs from a fresh shell, without setting up the area")
except KeyError:
    pass
sample = options.sample
submit = options.submit
for jobId, file_to_process in zip(jobIds, files_to_process):
    jobname = sample+'_'+jobId
    jobname += (options.label if options.label else '')
    bsubCmd = ("bsub "
               +" -q %s"%queue
               +" -J %s"%jobname
               +" %s"%batchScript
               +" %s"%file_to_process
               +" %s"%sample
               +" %s"%output_dir
               +" %s"%jobId
               +" %s"%rootcorebin)
               
    print bsubCmd
    if submit :
        os.system(bsubCmd)
        time.sleep(1)

#
