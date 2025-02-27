SHELL := /bin/bash
dirname := $(notdir $(patsubst %/,%,$(CURDIR)))
project_name = eligibility-signposting-api

list:
	@grep '^[^#[:space:]].*:' Makefile

build:
	docker build -t $(project_name) -f Dockerfile .

run: build
	docker run --rm -it -p 9000:9000 --name $(project_name) $(project_name)

clean:
	rm -rf ./node_modules

install:
	npm install --dev

update:
	npm update

spec:
	make -C .. publish

test:
	NODE_ENV=test npx mocha --reporter spec

test-report:
	NODE_ENV=test npx mocha --reporter mocha-junit-reporter --reporter-options mochaFile=../../reports/tests/$(dirname).xml || true

.PHONY: build run spec
