#!/bin/bash
root_dir="$1"
shift
corpus="$1"
shift
environment="$root_dir/testing"
corpnames="$@"
corptar="export/$corpus.tar.xz"
rm -f "$environment/chroot/.in/${corptar##export/}"
ln "$corptar" "$environment"/chroot/.in/
for corpus in $corpnames
do
    hsh-run --rooter "$environment" -- rm -rf "/var/lib/manatee/{data,registry,vert}/$corpus"
done
hsh-run --rooter "$environment" -- tar --no-same-permissions --no-same-owner -xJvf "${corptar##export/}" --directory /var/lib/manatee
for corpus in $corpnames
do
    hsh-run --rooter "$environment" -- /bin/sh -c "export MANATEE_REGISTRY=/var/lib/manatee/registry && mksizes $corpus"
done
