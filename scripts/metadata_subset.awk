BEGIN { OFS = "\t"; FPAT="([^,]*)|(\"[^\"]+\")"; file = "filename-id.vert" }

{ print $1, $13 > file }
