
#
# Script to run TruthPlot on a single file on the batch
#
# This script can be tested with the following command:
#   $ source run_TruthPlot.sh <parameters>
# and submitted to lxbatch with submit_lxbatch.py.
#
# davide.gerbaudo@gmail.com
# Jul 2015

INPUT_FILE=$1
SAMPLE=$2
OUTPUT_DIR=$3
JOBID=$4
TMP_ROOTCOREBIN=$5

# set -e # exit on error
# set -u # exit on undefined variable

echo "Using these options:"
echo "INPUT_FILE       $INPUT_FILE     "
echo "SAMPLE           $SAMPLE         "
echo "OUTPUT_DIR       $OUTPUT_DIR     "
echo "JOBID            $JOBID          "
echo "TMP_ROOTCOREBIN  $TMP_ROOTCOREBIN"

# todo: can I rely on ROOTCOREBIN or should I spell it out?
BASE_DIR='/afs/cern.ch/work/g/gerbaudo/public/samesign_jets/ttVsystematics/make_plots'
# BASE_DIR='${TMP_ROOTCOREBIN}/..'


DEST_DIR="${BASE_DIR}/${OUTPUT_DIR}"
OUT_LOCAL_FILE="${OUTPUT_DIR}/hist-${SAMPLE}.root"
OUT_REMOTE_FILE="${DEST_DIR}/hist-${SAMPLE}-${JOBID}.root"

WORK_DIR=$(pwd)
echo "Working in ${WORK_DIR} with the following options"
# echo "LSF Job ID : ${LSF_JOBID}" # undefined?
date

echo "Using the input file ${INPUT_FILE}"
echo "Setting up root"
# export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
# source $ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
cd ${BASE_DIR}
echo "Now in `pwd`"
# echo "source ${BASE_DIR}/RootCoreBin/local_setup.sh"
# source ${BASE_DIR}/RootCoreBin/local_setup.sh
# echo "source RootCoreBin/local_setup.sh"
# source RootCoreBin/local_setup.sh
echo "sourcing"
source /afs/cern.ch/work/g/gerbaudo/public/samesign_jets/ttVsystematics/make_plots/RootCoreBin/local_setup.sh
echo "Using root `root-config --version` from `which root`"
cd ${WORK_DIR}

echo "${INPUT_FILE}" > filelist.txt
echo "mkdir -p ${OUTPUT_DIR}"
echo "rmdir    ${OUTPUT_DIR}"
mkdir -p ${OUTPUT_DIR}
rmdir    ${OUTPUT_DIR} # drop the innermost dir, leave top-level ones

TruthPlot --filelist filelist.txt --sample-name ${SAMPLE} -o ${OUTPUT_DIR} -n 10

echo "Done `date`"
ls -ltrh
mkdir -p ${DEST_DIR}/
cp -p ${OUT_LOCAL_FILE} ${OUT_REMOTE_FILE}
# no need to cleanup, lsf will do it
echo "Done (`date`)"
