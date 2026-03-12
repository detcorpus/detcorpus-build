DOCKERHOST := detcorpus
noskeimage := daakhmerov/noske-pushdom:latest
localarch := export
remoteroot := corpora
remotearch := setup
corplist = $(corpora)
configfiles := $(patsubst %,config/%,$(corplist)) 
corpvertfiles := $(wildcard $(localarch)/vert/*.vert)
subcfiles := config/detcorpus-fiction.subcorpora
archfile := detcorpus.tar.xz 
exportfiles := $(patsubst config/%,$(localarch)/registry/%,$(configfiles) $(subcfiles)) $(corpvertfiles)
exportdirs := $(patsubst %,$(localarch)/%,registry vert)
packed := $(localarch)/$(archfile)


$(localarch)/registry/% : config/%
	test -d $(@D) || mkdir -p $(@D)
	cp -f $< $@

deploy: $(exportfiles)
	docker run -dit --name $(corpsite) -v $$(pwd)/$(localarch)/vert:/var/lib/manatee/vert -v $$(pwd)/$(localarch)/registry:/var/lib/manatee/registry -p $(IP):$(PORT):8080 -e CORPLIST="$(corplist)" $(noskeimage)

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
	ssh $(DOCKERHOST) 'docker run -dit --name testing -v $$(pwd)/$(remoteroot)/vert:/var/lib/manatee/vert -v $$(pwd)/$(remoteroot)/registry:/var/lib/manatee/registry -p 127.0.0.1:8088:8080 -e CORPLIST="$(corplist)" $(noskeimage)'
