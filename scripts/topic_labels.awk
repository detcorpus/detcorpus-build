BEGIN { OFS = "\t"; model_n = 1 }

{ while ( model_n <= ARGC - 2 ) { if ( NR==FNR ) { labels[$2,model_n] = $3; next } else { model_n += 1; NR = 0; FNR = 0 } } }
$1 ~ /#/ { next }
{ out = $1 OFS $2 OFS $3 OFS $4 OFS $5; for ( i = 6; i <= NF; i++ ) { out = out OFS $i "_" labels[$i,i-5] }; print out }
