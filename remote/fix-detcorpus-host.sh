#!/bin/sh
environment="testing"
hsh-run --root "$environment" -- sed -i '/URL_BONITO/s/localhost/detcorpus.ru/' /var/www/crystal/config.js
