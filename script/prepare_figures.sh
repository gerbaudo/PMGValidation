#!/bin/bash

# prepare the files for Josh and Maria
# first get them from
#   scp -r uclhc-1.ps.uci.edu:/data/uclhc/uci/user/gerbaudo/ss3l/ttVsystematics/make_plots/trashbin/dummy /tmp/

DESTINATION_DIR="plots_ttV_syst_2016-01-11"
for EXT in eps png
do
    mkdir -p ${DESTINATION_DIR}/meff
    mkdir -p ${DESTINATION_DIR}/njet
    mv dummy/c_ttV_syst_h_jetN.$EXT ${DESTINATION_DIR}/njet/ttw_sys_scale.$EXT
    mv dummy/c_ttV_syst_h_meff.$EXT ${DESTINATION_DIR}/meff/ttw_sys_scale.$EXT
done
tar cf ${DESTINATION_DIR}.tar ${DESTINATION_DIR}
