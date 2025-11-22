#!/usr/bin/env bash

# Do not run this directly!
# Please use the provided install.py

bin=$1
lib=$2

if [[ $UID == 0 ]];then
  echo "installing python-sat"
  echo "creating libraries in $lib"
  # create the libraries 
  mkdir -p "$lib"
  echo "copying sat/modules to $lib"
  cp -rf ./sat/modules "$lib"
  # create the binary
  echo "creating the binary in $bin/sat"
  mkdir -p "$bin"
  cp -f ./sat/sat.py "$bin"/sat
else
  echo "$UID"
  echo "Please install with python-sat!"
fi
