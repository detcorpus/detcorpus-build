BEGIN { OFS = "\t" }

NR==FNR { count_f1[$3]++; state[$2,$3,count_f1[$3],1] = $4; state[$2,$3,count_f1[$3],2] = $5; state[$2,$3,count_f1[$3],3] = $6; next }
$1 ~ /<doc/ { print; next }
$1 ~ /<f/ { match($2, /id=([0-9]+)/, mtch); f_id = mtch[1]; print; next }
{ count_f2[$2]++; print $0, state[f_id,$2,count_f2[$2],1], state[f_id,$2,count_f2[$2],2], state[f_id,$2,count_f2[$2],3]; next }
