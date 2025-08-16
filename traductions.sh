#!/usr/bin/bash

DEST="${1:-i18n}"
echo "destination: $DEST"

readarray -d '' plugins < <(find "msm_ng/modules/" -depth -name "plugin.py" -print0)

langs=("fr" "es")
for lg in ${langs[@]}; do

    echo "# $lg ..."
    mkdir -p "i18n/$lg/LC_MESSAGES/"
    mkdir -p "$DEST/$lg/LC_MESSAGES/"
    /usr/lib/qt6/bin/lupdate -locations relative "msm_ng/__main__.py" "msm_ng/modules/_plugin/base.py" -source-language $lg -ts "i18n/$lg/LC_MESSAGES/msm_$lg.ts"
    /usr/lib/qt6/bin/lrelease "i18n/$lg/LC_MESSAGES/msm_$lg.ts" -qm "$DEST/$lg/LC_MESSAGES/msm_$lg.qm"

    for fic in "./msm_ng/modules/"*; do
        fic=${fic##*/}
        if [[ ${fic:0:1} != "_" ]] && [ -e "msm_ng/modules/$fic/plugin.py" ]; then
            #echo " **** $fic ..."
            readarray -d '' plugins < <(find "msm_ng/modules/$fic/" -depth -name "*.py" -print0)
            /usr/lib/qt6/bin/lupdate -locations relative ${plugins[*]} -source-language $lg -ts "i18n/$lg/LC_MESSAGES/msm_${fic}_$lg.ts"
            /usr/lib/qt6/bin/lrelease "i18n/$lg/LC_MESSAGES/msm_${fic}_$lg.ts" -qm "$DEST/$lg/LC_MESSAGES/msm_${fic}_$lg.qm"
        fi
    done
    echo

done
