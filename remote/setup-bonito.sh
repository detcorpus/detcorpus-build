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
sed -i "/Alias/s/bonito/$corpname-testing/" /etc/httpd2/conf/sites-available/"$corpname"-testing.conf
sed -i "s,/var/www/bonito\?,/var/www/$corpname," /etc/httpd2/conf/sites-available/"$corpname"-testing.conf
sed -i "/#ServerName/s/#ServerName\s+www.example.com:80/ServerName localhost:80/" /etc/httpd2/conf/sites-available/default.conf
mkdir -p "$corpdir"
a2ensite "$corpname"-testing
# setup bonito instance
setupbonito "$corpdir" /var/lib/manatee
cgifile="$corpdir/run.cgi"
if $(grep -q "corplist = \[u'susanne'\]" $cgifile)
then
	sed -i "/corplist = \[u'susanne'\]/s/\[u'susanne'\]/[$pycorplist]/" "$cgifile"
else
	sed -i "/[^:] corplist =/s/\[\([^]]\+\)\]/[\1$pycorplist]/" "$cgifile"
fi
# deduplicate corpus list
dedupcorplist="$(sed -n '/[^:] corplist =/s/^.*\[\([^]]\+\)\].*$/\1/p' $cgifile | awk 'BEGIN{FS=" "}{for (i=1;i<=NF;i++) if (!a[$i]++) printf "%s ", $i}')"
sed -i "/corplist =/s/\[\([^]]\+\)\]/[$dedupcorplist]/" "$cgifile"
# set default corpus (only first timme application)
sed -i "/corpname =/s/u'susanne'/u'$defaultcorp'/" "$cgifile"
sed -i "/os.environ\['MANATEE_REGISTRY'\]/s/''/'\/var\/lib\/manatee\/registry'/" "$cgifile"
# setup crystal instance
cp /etc/httpd2/conf/sites-available/bonito.conf /etc/httpd2/conf/sites-available/crystal.conf
sed -i "s/bonito/crystal/g" /etc/httpd2/conf/sites-available/crystal.conf
a2ensite crystal
sed -i '/URL_BONITO/s/https/http/' /var/www/crystal/config.js
sed -i "/URL_BONITO/s/bonito/$corpname-testing/" /var/www/crystal/config.js


