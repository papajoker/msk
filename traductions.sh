#!/usr/bin/bash

langs=("fr" "es")
for lg in ${langs[@]}; do
    echo "i18n/$lg/LC_MESSAGES/ ..."
    mkdir -p "i18n/$lg/LC_MESSAGES/"
    /usr/lib/qt6/bin/lupdate -recursive -locations relative "msm_ng/__main__.py" "msm_ng/modules/_plugin/base.py" -source-language $lg -ts "i18n/$lg/LC_MESSAGES/msm_$lg.ts"
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

    #find "msm_ng/modules/" -name \*.py -exec /usr/lib/qt6/bin/lupdate -locations relative '{}' -source-language $lg -ts "i18n/$lg/LC_MESSAGES/msm_modules_$lg.ts" \;
    #/usr/lib/qt6/bin/lrelease "i18n/$lg/LC_MESSAGES/msm_modules_$lg.ts" -qm "i18n/$lg/LC_MESSAGES/msm_modules_$lg.qm"
done

exit 0
