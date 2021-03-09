options(java.parameters = "-Xmx4096m")
library(rJava)
# install_github("mimno/RMallet/mallet")
# mallet version with mallet.topic.load function is required
library(mallet)
library(LDAvis)
library(readr)
library(servr)
library(optparse)

parser <- OptionParser()
parser <- add_option(parser, c("-m", "--model"),
                     help = "Input mallet model")
parser <- add_option(parser, c("-v", "--vocabulary"),
                     help = "Input vocabulary")
parser <- add_option(parser, c("-o", "--outdir"), 
                     help = "Output directory")
args <- parse_args(parser)

main <- function(args) {
  topic.model <- mallet.topic.load(args$model)
  topic.words <- mallet.topic.words(topic.model, smoothed = T, normalized = T)
  doc.topics <- mallet.doc.topics(topic.model, smoothed = T, normalized = T)
  
  word.freqs <- read_tsv(args$vocabulary, col_names = c("token", "freq", "doc freq"))
  vocabulary <- word.freqs$token
  
  doc.tokens <- rowSums(mallet.doc.topics(topic.model, normalized = F, smoothed = F))
  
  json <- createJSON(phi = topic.words,
                     theta = doc.topics,
                     doc.length = doc.tokens,
                     vocab = vocabulary,
                     term.frequency = word.freqs$freq)
  
  serVis(json, out.dir = args$outdir, open.browser = F)
}

main(args)


