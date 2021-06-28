BEGIN { OFS = "\t"; FPAT="([^,]*)|(\"[^\"]+\")" }

{ print $1, $13 }
