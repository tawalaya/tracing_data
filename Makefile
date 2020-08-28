define PROJECT_HELP_MSG

Usage:
    make help                   show this message
    make clean                  remove intermediate files (see CLEANUP)

    make fonts                  checks embedded fonts in all generated figures

    make start                  launch a jupyter server from the local virtualenv

endef
export PROJECT_HELP_MSG

help:
	echo $$PROJECT_HELP_MSG 

fonts:
	for i in images/*.pdf; do echo "$${i}:" >> fonts.log && pdffonts $$i >> fonts.log; done && less fonts.log && rm fonts.log

start:
	jupyter notebook .

CLEANUP = *.pyc

clean:
	rm -rf ${CLEANUP}

.PHONY: help start clean fonts
