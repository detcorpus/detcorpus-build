# SETUP PATHS
ROOT=..
SRC=$(ROOT)/detcorpus
vpath %.txt $(SRC)
vpath %.fb2 $(SRC)
vpath %.html $(SRC)
vpath %.csv $(SRC)
vpath %.epub $(SRC)
vpath %.md $(SRC)
_dummy := $(shell mkdir -p lda)
#
# SETUP CREDENTIALS
HOST=detcorpus
# CHROOTS
TESTING=testing
PRODUCTION=production
ROLLBACK=rollback
TESTPORT=8098
PRODPORT=8099
BUILT=built
RSYNC=rsync -avP --stats -e ssh
#
## corpora
corpbasename := detcorpus
corpsite := detcorpus
corpora := detcorpus-fiction detcorpus-nonfiction
corpora-vert := $(addsuffix .vert, $(corpora))
## Remote corpus installation data
corpsite-detcorpus := detcorpus
corpora-detcorpus := detcorpus-fiction detcorpus-nonfiction
#
#
## SETTINGS
SHELL := /bin/bash
NPROC := $(shell nproc)
.PRECIOUS: %.txt %.conllu %.wlda.vert detcorpus.vocab.txt detcorpus.vert
udmodel := data/russian-syntagrus-ud-2.5-191206.udpipe
numtopics := 100 200 300
metadatadb=$(SRC)/metadata.sql
randomseed := $(SRC)/random.seed
random := $(file <$(randomseed))


## UTILS
gitsrc=git --git-dir=$(SRC)/.git/
db2meta=python3 scripts/db2meta.py --dbfile=meta.db 
udpiper := PYTHONPATH=../udpiper python3 ../udpiper/bin/udpiper 

## HARDCODED FILELIST TWEAKS
duplicatesrc := $(shell $(gitsrc) ls-files dups)
skipfiles := emolemmas.txt emowords.txt $(shell $(gitsrc) ls-files depot oldscripts algfio docs) 
## STANDARD SOURCE FILELISTS
gitfiles := $(shell $(gitsrc) ls-files)
srcfiles := $(filter-out $(duplicatesrc) $(skipfiles), $(gitfiles))
txtfiles := $(filter %.txt, $(srcfiles))
srchtmlfiles := $(filter %.html, $(srcfiles))
srctxtfiles := $(filter-out $(fb2files:.fb2=.txt) $(srchtmlfiles:.html=.txt), $(txtfiles))
srcfb2files := $(filter %.fb2, $(srcfiles))
srcepubfiles := $(filter %.epub, $(srcfiles))
textfiles := $(srctxtfiles) $(srcfb2files) $(srchtmlfiles) $(srcepubfiles)
vertfiles := $(srcfb2files:.fb2=.vert) $(srctxtfiles:.txt=.vert) $(srchtmlfiles:.html=.vert) $(srcepubfiles:.epub=.vert)

help:
	 @echo 'Makefile for building detcorpus                                           '
	 @echo '                                                                          '
	 @echo 'Corpus texts source files are expected to be found at: $(SRC)             '
	 @echo '                                                                          '
	 @echo '                                                                          '
	 @echo 'Dependencies: git, python, w3m, awk, mystem,                              '
	 @echo '              pandoc, docker                                              '
	 @echo '                                                                          '
	 @echo 'Usage:                                                                    '
	 @echo '   make convert	     convert all sources (fb2, html) into txt             '
	 @echo '   make compile      prepare vertical files of all corpora                '
	 @echo '                                                                          '
	 @echo '   make docker-local compile and run corpus in a local docker image       '
	 @echo '                     the corpus site will be available at 127.0.0.1:8088  '        
	 @echo '                                                                          '

## remote operation scripts
include docker.mk

print-%:
	@echo $(info $*=$($*))

%.txt: %.fb2 
	test -d $(@D) || mkdir -p $(@D)
	pandoc -t plain -o $@ $<

%.txt: %.epub
	pandoc -o $@ $<

%.txt: %.html
	test -d $(@D) || mkdir -p $(@D)
	w3m -dump $< > $@

%.vert: %.txt scripts/mystem2vert.py
	test -d $(@D) || mkdir -p $(@D)
	sed -e 's/<pb n="\([0-9]\+\)"\/\?>/ PB\1/g' \
		-e "s/\(\w\+\)'\(\w\+\)/\1ъ\2/g" \
		-e 's/&#769;//g' -e 's/&#8209;|‑/-/g' $< | mystem -n -d -i -g -c -s --format xml | sed 's/[^[:print:]]//g' | python3 scripts/mystem2vert.py $@ > $@

meta.db: $(metadatadb)
	test -f $@ && rm -f $@ || :
	sqlite3 $@ < $<

.mrc: meta.db
	test -d mrc || mkdir mrc
	sqlite3 meta.db "select download_link || ' mrc/' || book_id || '.mrc' from books where download_link is not null" | fgrep -v search.rsl | while read link outfile ; do test -f "$$outfile" || wget "$$link" -O "$$outfile" ; done && touch .mrc

define NL


endef

.metadata: $(textfiles) $(vertfiles) meta.db $(SRC)/genres.csv scripts/db2meta.py
	$(foreach f, $(textfiles), sed -i -e "1c $$($(db2meta) -f $(f))" $(basename $(f)).vert$(NL))
	touch $@

meta.csv: meta.db scripts/db2meta.py
	$(db2meta) -o $@

metadata.csv: meta.db scripts/db2meta.py
	$(db2meta) -o $@ --dataset

detcorpus.vert: $(vertfiles) .metadata
	@echo $(file >$@) $(foreach O,$(sort $^),$(file >>$@,$(file <$O)))
	@true

detcorpus.wlda.vert: $(vertfiles:.vert=.wlda.vert)
	$(file >$@) $(foreach O,$(sort $^),$(file >>$@,$(file <$O)))
	@true

detcorpus-nonfiction.vert: detcorpus.wlda.vert
	gawk -v mode=nonfic -f scripts/ficnonfic.gawk $< > $@

detcorpus-fiction.vert: detcorpus.wlda.vert
	gawk -v mode=fic -f scripts/ficnonfic.gawk $< > $@

compile: $(corpora-vert)

convert: $(vertfiles:.vert=.txt) 

## LDA

%.slem: %.vert
	gawk -f scripts/vert2lemfragments.gawk $< > $@

%.vectors: %.slem stopwords.txt
	mallet import-file --line-regex "^(\S*\t[^\t]*)\t([^\t]*)\t([^\t]*)" --label 3 --name 1 --data 2 --keep-sequence --token-regex "[\p{L}\p{N}-]*\p{L}+" --stoplist-file stopwords.txt --input $< --output $@

lda/model%.mallet lda/summary%.txt lda/doc-topics%.txt lda/topic-phrase%.xml lda/diag%.xml: detcorpus.vectors
	mallet train-topics --input $< --num-topics $* --output-model lda/model$*.mallet \
		--num-threads $(NPROC) --random-seed 41 --num-iterations 1000 --num-icm-iterations 20 \
		--num-top-words 50 --optimize-interval 20 \
		--output-topic-keys lda/summary$*.txt \
		--xml-topic-phrase-report lda/topic-phrase$*.xml \
		--output-doc-topics lda/doc-topics$*.txt --doc-topics-threshold 0.05 \
		--diagnostics-file lda/diag$*.xml

ldadir:
	test -d lda || mkdir -p lda

lda: $(patsubst %, lda/model%.mallet, $(numtopics)) | ldadir

%.wlda.vert: %.vert $(patsubst %, lda/labels%.txt, $(numtopics)) $(patsubst %,lda/doc-topics%.txt,$(numtopics))
	python3 scripts/addlda2vert.py -l $(patsubst %,lda%,$(numtopics)) -t $(patsubst %,lda/labels%.txt,$(numtopics)) -d $(patsubst %,lda/doc-topics%.txt,$(numtopics)) -i $< -o $@

## Dataset

shuffled := $(addprefix data/text/, $(vertfiles))
ldafilelist := lda/summary*.txt lda/diag*.xml lda/doc-topics*.txt lda/labels*.txt lda/topic-phrase*.xml
ldafiles := $(foreach ntopics,$(numtopics),$(subst *,$(ntopics),$(ldafilelist)))
docfiles := README.md CHANGELOG.md metadata.csv
testfiles := test/metadata.py test/lda.py
txtzip := texts.zip
datasetfiles := $(ldafiles) $(docfiles) $(testfiles) $(txtzip) 

data/text/%.vert: %.wstate.vert $(randomseed)
	test -d $(@D) || mkdir -p $(@D)
	python3 scripts/shuffle_vert.py -r $(random) $< $@

texts.zip: $(shuffled)
	rm -f $@
	rm -f $(filter-out $(shuffled),$(wildcard data/text/*s/*))
	zip -r -D $@ data/text/

dataset.zip: $(datasetfiles)
	zip -r $@ $<

dataset: dataset.zip

## TESTS

test: test-dataset

test-dataset: test-metadata test-lda

test-metadata: metadata.csv texts.zip
	python3 test/metadata.py

test-lda: metadata.csv $(patsubst %,lda/doc-topics%.txt,$(numtopics))
	python3 test/lda.py

## CLEANUP FOR BUILD

clean: clean-converted

clean-converted:
	$(foreach f, $(vertfiles), rm -f $(f:.vert=.txt)$(NL))

clean-build:
	$(foreach f, $(vertfiles), rm -f $(f)$(NL))
