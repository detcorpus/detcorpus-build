BEGIN { OFS = "\t"; file = 1 }

{ while ( file == 1 ) { if ( NR==FNR ) { ids[$1] = $2; next } else { file = file + 1; NR = FNR = 0 } } }
{ while ( file == 2 ) { if ( NR==FNR ) { file_ids[$2] = $1; next } else { file = file + 1 } } }
$1 ~ /^#/ { next }
$1 in ids { if ( doc_id != ids[$1] ) { f_id = 1; doc_f_id = $1; doc_id = ids[$1]; close(file) } else { if (doc_f_id != $1) { doc_f_id = $1; f_id = f_id + 1 } }; file = ( substr(file_ids[doc_id], 1, match(file_ids[doc_id], /\.([^.]*)$/) ) "state.vert" ); print doc_id, f_id, $5, $6, $7, $8 > file }
