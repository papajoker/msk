#!/usr/bin/bash

readarray -d '' plugins < <(find "msm_ng/modules/" -depth -name "plugin.py" -print0)

langs=("fr" "es")
for lg in ${langs[@]}; do

    echo "i18n/$lg/LC_MESSAGES/ ..."
    mkdir -p "i18n/$lg/LC_MESSAGES/"
    /usr/lib/qt6/bin/lupdate -locations relative ${plugins[*]} "msm_ng/__main__.py" "msm_ng/modules/_plugin/base.py" -source-language $lg -ts "i18n/$lg/LC_MESSAGES/msm_$lg.ts"
    /usr/lib/qt6/bin/lrelease "i18n/$lg/LC_MESSAGES/msm_$lg.ts" -qm "i18n/$lg/LC_MESSAGES/msm_$lg.qm"

    for fic in "./msm_ng/modules/"*; do
        fic=${fic##*/}
        if [[ ${fic:0:1} != "_" ]] && [ -e "msm_ng/modules/$fic/plugin.py" ]; then
            echo " **** $fic ..."

            readarray -d '' array < <(find "msm_ng/modules/$fic/" -depth -name "*.py" ! -name 'plugin.py' -print0)
            echo "    # "${array[*]}
            /usr/lib/qt6/bin/lupdate -locations relative ${array[*]} -source-language $lg -ts "i18n/$lg/LC_MESSAGES/msm_${fic}_$lg.ts"
            /usr/lib/qt6/bin/lrelease "i18n/$lg/LC_MESSAGES/msm_${fic}_$lg.ts" -qm "i18n/$lg/LC_MESSAGES/msm_${fic}_$lg.qm"
        fi
    done
    echo

done
