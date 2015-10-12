#!/bin/env bash

# copy files downloaded locally from /tmp to eos
#
# davide.gerbaudo@gmail.com
# 2015-09-18

set -eu

function help() {
    local exe="copy_from_tmp_to_eos.sh"
    echo "${exe} input/ output/"
    echo ""
    echo "Example usage:"
    echo "${exe} /tmp/dataset_foo/ /eos/atlas/user/g/gerbaudo/tmp/"
    echo ""
    echo "This will copy the directory and its root files to the destination"
}

function copy_from_tmp_to_eos() {
    local orig=$1
    local dest=$2
    local eos="/afs/cern.ch/project/eos/installation/atlas/bin/eos.select"
    local xrdcp="xrdcp"
    # eos="echo eos"      # uncommment here to debug
    # xrdcp="echo xrdcp"  # 
    local sample_name=$(basename ${orig})
    local file_name=""
    local X=""

    ${eos} mkdir ${dest}/${sample_name}
    for X in $(find ${orig} -name "*.root*")
    do
        file_name=`basename ${X}`
        echo ${file_name}
        ${xrdcp} ${X} root://eosatlas.cern.ch/${dest}/${sample_name}/${file_name}
    done

    local filelist="list_eos_${sample_name}.txt"
    touch ${filelist}
    for X in $(${eos} ls ${dest}/${sample_name})
    do
        echo "root://eosatlas.cern.ch/${dest}/${sample_name}/${X}" >> ${filelist}
    done
    echo "Filelist saved to ${filelist}"
    
}

function main() {
    if [ "$#" -eq 2 ]
    then
        local orig=$1
        local dest=$2
        copy_from_tmp_to_eos ${orig} ${dest}
    else
        help
    fi
}

main $*