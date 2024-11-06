DOCKERHOST := detcorpus
localarch := export
remoteroot := corpora
remotearch := setup
corplist = $(corpora) 
configfiles := $(patsubst %,config/%,$(corplist)) 
corpvertfiles := $(patsubst %,%.vert,$(corplist))
subcfiles := config/detcorpus-fiction.subcorpora
archfile := detcorpus.tar.xz 
exportfiles := $(patsubst config/%,$(localarch)/registry/%,$(configfiles) $(subcfiles)) $(patsubst %,$(localarch)/vert/%,$(corpvertfiles))
exportdirs := $(patsubst %,$(localarch)/%,registry vert)
packed := $(localarch)/$(archfile)

$(localarch)/registry/% : config/%
	test -d $(@D) || mkdir -p $(@D)
	cp -f $< $@

$(localarch)/vert/% : %
	test -d $(@D) || mkdir -p $(@D)
	cp -f $< $@

pull-image:
	docker pull maslinych/noske-alt:2.142-alt1

docker-cleanup:
	test -z "$(shell docker ps -aq -f status=exited -f name=$(corpsite))" || @echo docker rm $(corpsite)

docker-local: $(exportfiles) | docker-cleanup
	if [ ! "$(shell docker ps -a -q -f name=$(corpsite))" ]; then \
	docker run -dit --name $(corpsite) -v $$(pwd)/$(localarch)/vert:/var/lib/manatee/vert -v $$(pwd)/$(localarch)/registry:/var/lib/manatee/registry -p 127.0.0.1:8088:8080 -e CORPLIST="$(corplist)" maslinych/noske-alt:2.142-alt1 ;\
	else \
	@echo "Detcorpus is already running in a local docker container. Stop it first to run anew" ;\
	fi


$(packed) : $(exportfiles)
	rm -f $@
	pushd $(localarch); tar cJvf $(archfile) registry vert

pack-files: $(packed)

upload-files: $(packed)
	rsync -avP -e ssh $< $(DOCKERHOST):$(remotearch)
	ssh $(DOCKERHOST) 'tar xvf $(remotearch)/$(archfile) -C $(remoteroot)'

remove-testing-docker:
	ssh $(DOCKERHOST) 'docker stop testing'
	ssh $(DOCKERHOST) 'docker rm testing'

create-testing-docker: 
	ssh $(DOCKERHOST) 'docker run -dit --name testing -v $$(pwd)/$(remoteroot)/vert:/var/lib/manatee/vert -v $$(pwd)/$(remoteroot)/registry:/var/lib/manatee/registry -p 127.0.0.1:8088:8080 -e CORPLIST="$(corplist)" maslinych/noske-alt:2.130.1-alt4-1'

