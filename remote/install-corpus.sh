#!/bin/bash
repo="$1"
shift
rootdir="$1"
shift
corpus="$1"
shift
environment="$rootdir/testing"
corptar="$corpus.tar.xz"
rm -f "$environment/chroot/.in/$corptar"
ln "$repo/$corptar" "$environment"/chroot/.in/
corpnames="$(cat $repo/${corptar%%.tar.xz}.setup.txt | cut -d' ' -f2-)"
for corpus in $corpnames
do
    hsh-run --rooter "$environment" -- rm -rf "/var/lib/manatee/{data,registry,vert}/$corpus"
done
hsh-run --rooter "$environment" -- tar --no-same-permissions --no-same-owner -xJvf "$corptar" --directory /var/lib/manatee
for corpus in $corpnames
do
    hsh-run --rooter "$environment" -- /bin/sh -c "export MANATEE_REGISTRY=/var/lib/manatee/registry && mksizes $corpus"
done
