#!/bin/bash
sirius_dir=$(dirname $0)
source ../run_env.env

mkdir -p logs
env_list=( BEARER_TOKEN ORENJI_URL GIT_PAT LC_USR LC_PW STEAM_KEY MIRAI_KEY QQ_ACCOUNT )
for env_name in ${env_list[@]}; do
    if [ -z "${!env_name}" ]; then
        read -p "Enter $env_name: " value
        export $env_name="$value"
    fi
done

cd $sirius_dir/sirius
message=
while true; do
    python3 sirius.py $message
    rc=$?
    if [ $rc -eq 0 ]; then
        exit $rc
    elif [ $rc -ge 2 ]; then
        branch=$(git branch --show-current)
        message="$rc $branch"
        continue
    fi
done
