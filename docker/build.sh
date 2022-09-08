#!/bin/bash
function error() {
    echo "Missing input"
    exit 1
}

pat=$1
branch=$2
[ -z "${pat}" ] && error
[ -z "${branch}" ] && error

name='rumina'
build_arg1="GIT_PAT=${pat}"
build_arg2="BRANCH=${branch}"
docker build -t ${name} --build-arg ${build_arg1} --build-arg ${build_arg2} .
