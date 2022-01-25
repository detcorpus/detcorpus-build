#!/bin/sh
root_dir="$1"
shift
site="$1"
shift
environment="$root_dir/testing"
corplist="$@"
cp ~/bin/setup-bonito.sh "$environment"/chroot/.in/
hsh-run --rooter "$environment" -- sh -x setup-bonito.sh $site $corplist
