BEGIN { OFS = "\t" }

NR==FNR { ids[$1] = $2; next }
$1 ~ /^#/ { next }
$1 in ids { if ( doc_id != ids[$1] ) { f_id = 1; doc_f_id = $1; doc_id = ids[$1]; close(file) } else { if (doc_f_id != $1) { doc_f_id = $1; f_id = f_id + 1 } }; file = ( outdir "/" doc_id ".state.vert"); print doc_id, f_id, $5, $6, $7, $8 > file }
