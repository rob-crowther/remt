RSYNC=rsync -zcav \
	--exclude=\*~ --exclude=.\* \
	--delete-excluded --delete-after \
	--no-owner --no-group \
	--progress --stats


doc: .sphinx-stamp

doc-upload:
	$(RSYNC) build/doc/ wrobell@dcmod.org:~/public_html/remt

.sphinx-stamp:
	PYTHONPATH=. sphinx-build doc build/doc
	PYTHONPATH=. sphinx-build -b latex doc build/latex
	make -C build/latex
