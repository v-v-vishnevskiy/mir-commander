#!/usr/bin/env bash

sargs=("$@")

currentDir=$(pwd)
thisDirName=$(dirname "$0")
cd "$thisDirName" || exit 1
mircmdDir=$(pwd)
cd "$currentDir" || exit 1

if [ -z "$MIRCMD_ROOT_DIR" ]; then
    export MIRCMD_ROOT_DIR=$mircmdDir
fi


source "${MIRCMD_ROOT_DIR}/.venv/bin/activate"


declare -a uargs
for ((i=0; i < ${#sargs[@]}; i++))
do
    item=${sargs[i]}
    case "${item}" in
        --wrapper)
            ((i++))
            wrapper="${sargs[i]}"
            ;;
        --wrapper=*)
            wrapper="${item#*=}"
            ;;
        *)
            uargs[${#uargs[@]}]="${item}"
            ;;
    esac
done


PYTHONPATH="${MIRCMD_ROOT_DIR}" $wrapper python "$MIRCMD_ROOT_DIR/mir_commander" "${uargs[@]}"
