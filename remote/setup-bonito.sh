#!/bin/bash
corpname="$1"
corpdir="/var/www/$corpname"
shift
corplist="$@"
corpnames=($corplist)
defaultcorp="${corpnames[0]}"
for corp in ${corpnames[@]}
do
    pycorplist="$pycorplist u'$corp', "
done
# setup apache dir
cp /etc/httpd2/conf/sites-available/bonito.conf /etc/httpd2/conf/sites-available/"$corpname"-testing.conf
sed -i "s,/var/www/bonito\?,/var/www/$corpname," /etc/httpd2/conf/sites-available/"$corpname"-testing.conf
mkdir -p "$corpdir"
a2ensite "$corpname"-testing
# setup bonito instance
setupbonito "$corpdir" /var/lib/manatee
cgifile="$corpdir/run.cgi"
sed -i "s/\[u'susanne'\]/[$pycorplist]/" "$cgifile"
sed -i "s/u'susanne'/u'$defaultcorp'/" "$cgifile"
sed -i "/os.environ\['MANATEE_REGISTRY'\]/s/''/'\/var\/lib\/manatee\/registry'/" "$cgifile"
# setup crystal instance
cp /etc/httpd2/conf/sites-available/bonito.conf /etc/httpd2/conf/sites-available/crystal.conf
sed -i "s/bonito/crystal/g" /etc/httpd2/conf/sites-available/crystal.conf
a2ensite crystal
