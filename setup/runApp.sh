#!/bin/bash

MY_CWD=$(pwd)

# the installation folder is passed in as the only parameter
cd $1

mkdir -p "log"

cd load

python update_tables.py > "../log/$(date +"%Y_%m_%d_%I_%M_%p").log"

cd $MY_CWD

