OS = Linux

VERSION = 0.0.1

CURDIR = $(shell pwd)
SOURCEDIR = $(CURDIR)

ECHO = echo
RM = rm -rf
MKDIR = mkdir
FLAKE8 = flake8

setup:
	$(PIP_INSTALL) $(FLAKE8)

build:
	$(FLAKE8) $(SOURCEDIR) --show-source --statistics --count
