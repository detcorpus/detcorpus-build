BEGIN { OFS="\t"; cols["word"] = 1 ; cols["lemma"] = 2; cols["pos"] = 3 }

$1 ~ /<doc/ { match($0, /id="([^"]+)".* year="([^"]+)"/, mtch); doc_id = mtch[1]; year=mtch[2]; next }
$1 ~ /<f/ { delete count; match($2, /id=([0-9]+)/, mtch); f_id = mtch[1]; next }
$(cols[col]) != "" { count[$(cols[col])]++ }
$1 ~ /<\/f/ { for (w in count) { print year, doc_id, f_id, w, count[w] } }
