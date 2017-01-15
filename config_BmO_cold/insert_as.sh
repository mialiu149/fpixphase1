#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo usage: $0 disk alias
    exit 1
fi

disk=$1
ali=$2
hc=BpO

echo running write configs for disk $disk of HC ${hc}
python ${BUILD_HOME}/pixel/jmt/write_other_hc_configs.py $disk write

echo inserting detconfig, nametranslation, and portcardmap as alias $ali

${BUILD_HOME}/pixel/bin/PixelConfigDBCmd.exe --insertData detconfig ${hc}/detconfig/detectconfig.dat $ali
${BUILD_HOME}/pixel/bin/PixelConfigDBCmd.exe --insertData nametranslation ${hc}/nametranslation/translation.dat $ali
${BUILD_HOME}/pixel/bin/PixelConfigDBCmd.exe --insertData portcardmap ${hc}/portcardmap/portcardmap.dat $ali
