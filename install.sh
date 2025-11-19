#!/usr/bin/env bash

bin=$1
lib=$2

if [[ $UID == 0 ]];then
  echo "installing python-sat"
  echo "creating libraries in $lib"
  # create the libraries 
  mkdir -p "$lib"
  echo "copying sat/modues to $lib"
  cp -rf ./sat/modules "$lib"
  # create the binary
  echo "creating the binary in $bin"
  mkdir -p "$bin"
  cp -f ./sat/sat.py "$bin"
fi
