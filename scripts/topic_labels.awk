BEGIN { OFS = "\t"; model_n = 1 }

{ while ( model_n <= 3 ) { if ( NR==FNR ) { labels[$2,model_n] = $3; next } else { model_n += 1; NR = 0; FNR = 0 } } }
$1 ~ /#/ { next }
{ print $1, $2, $3, $4, $5, $6 "_" labels[$6,1], $7 "_" labels[$7,2], $8 "_" labels[$8,3] }
