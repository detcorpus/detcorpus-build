localroot := ~/hasher
localarch := export
remoteroot := .
remotearch := built

remote-setup:
	@echo Remote host: $(HOST)
	@echo Corpus archive basename: $(corpbasename)
	@echo Corpus site name: $(corpsite)
	@echo A list of corpora to be installed: $(corpora)

install-remote-scripts:
	$(RSYNC) remote/*.sh $(HOST):bin

create-testing: 
	ssh $(HOST) "bin/create-hsh.sh $(remoteroot)"
	ssh $(HOST) "bin/install-all-corpora.sh $(remotearch) $(remoteroot)"
	ssh $(HOST) "bin/setup-all-corpora.sh $(remotearch) $(remoteroot)"
	ssh $(HOST) "bin/fix-detcorpus-host.sh"

setup-bonito: 
	ssh $(HOST) "bin/setup-corpus.sh $(remoteroot) $(corpsite) $(corpora)"
	ssh $(HOST) "bin/fix-detcorpus-host.sh"

install-corpus-%: $(localarch)/%.tar.xz
	$(RSYNC) $< $(HOST):$(remotearch)/
	ssh $(HOST) "echo $(corpsite-$*) $(corpora-$*) > $(remotearch)/$*.setup.txt"
	ssh $(HOST) "bin/stop-env.sh $(remoteroot) testing"
	ssh $(HOST) "bin/install-corpus.sh $(remotearch) $(remoteroot) $*"
	ssh $(HOST) "bin/start-env.sh $(remoteroot) testing"

uninstall-testing:
	ssh $(HOST) "rm -f $(remotearch)/$(corpbasename).tar.xz"
	ssh $(HOST) "rm -f $(remotearch)/$(corpbasename).setup.txt"

start-%:
	ssh $(HOST) "bin/start-env.sh $(remoteroot) $*"

stop-%:
	ssh $(HOST) "bin/stop-env.sh $(remoteroot) $*"

update-corpus:
	make export
	make stop-testing
	make install-testing
	make start-testing

production: stop-production stop-testing
	ssh $(HOST) cp bin/testing2production.sh $(TESTING)/chroot/.in/
	ssh $(HOST) hsh-run --rooter $(TESTING) -- 'sh testing2production.sh $(corpsite) $(TESTPORT) $(PRODPORT)'
	ssh $(HOST) sh -c 'test -d $(ROLLBACK)/chroot && hsh --clean $(ROLLBACK) || echo empty rollback'
	ssh $(HOST) hsh --clean $(ROLLBACK) || :
	ssh $(HOST) rm -rf $(ROLLBACK)
	ssh $(HOST) mv $(PRODUCTION) $(ROLLBACK)
	ssh $(HOST) mv $(TESTING) $(PRODUCTION)
	$(MAKE) start-production

rollback: stop-production
	$(RSYNC) remote/testing2production.sh $(HOST):$(PRODUCTION)/chroot/.in/
	ssh $(HOST) hsh-run --rooter $(PRODUCTION) -- 'sh testing2production.sh $(PRODPORT) $(TESTPORT)'
	ssh $(HOST) sh -c 'test -d $(TESTING)/chroot && hsh --clean $(TESTING)'
	ssh $(HOST) rm -rf $(TESTING)
	ssh $(HOST) mv $(PRODUCTION) $(TESTING)
	ssh $(HOST) mv $(ROLLBACK) $(PRODUCTION)

install-scripts-local:
	$(RSYNC) remote/*.sh ~/bin


create-testing-local:
	sh ./remote/create-hsh.sh $(localroot)
	hsh-run --rooter $(localroot)/testing -- sh -x setup-bonito.sh $(corpsite) $(corpora)

install-local-%: $(localarch)/%.tar.xz
	sh ./remote/stop-env.sh $(localroot) testing
	echo "$(corpsite-$*) $(corpora-$*)" > $(localarch)/$*.setup.txt
	sh ./remote/install-corpus.sh $(localarch) $(localroot) $* 
	sh ./remote/start-env.sh testing

start-local:
	sh ./remote/start-env.sh $(localroot) testing

stop-local:
	sh ./remote/stop-env.sh $(localroot) testing 

