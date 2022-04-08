#!/bin/sh
corpname="$1"
shift
testport="$1"
shift
prodport="$1"
cp /etc/httpd2/conf/sites-available/bonito.conf /etc/httpd2/conf/sites-available/"$corpname".conf
sed -i "s,bonito,$corpname,g" /etc/httpd2/conf/sites-available/"$corpname".conf
a2ensite "$corpname"
a2dissite "$corpname"-testing
cd /etc/httpd2/conf/
cp ports-available/"$testport".conf ports-available/"$prodport".conf
sed -i "s/$testport/$prodport/g" ports-available/"$prodport".conf
a2disport "$testport"
a2enport "$prodport"
sed -i "/URL_BONITO/s,/$corpname-testing/,/$corpname/," /var/www/crystal/config.js
service httpd2 reload
