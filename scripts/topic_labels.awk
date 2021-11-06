BEGIN { OFS = "\t" }
fname != FILENAME { fname = FILENAME; idx++ }
idx <= 3 { labels[$2,idx] = $1 "_" $3 }
idx > 3 { print $1, $2, $3, $4, $5, labels[$6,1], labels[$7,2], labels[$8,3] }
