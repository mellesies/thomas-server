# `make` is expected to be called from the directory that contains
# this Makefile

TAG := latest

rebuild: clean build-dist

build-dist:
	# Increase the build number
	python inc-build.py thomas/server/__build__

	# Build the PyPI package
	python setup.py sdist bdist_wheel

publish-test:
	# Uploading to test.pypi.org
	twine upload --repository testpypi dist/*

publish:
	# Uploading to pypi.org
	twine upload --repository pypi dist/*

docker-image:
	# Building docker image
	# --------------------------------------------------------------------------
	# Rebuild the UI
	# --------------------------------------------------------------------------
	cd ../thomas-ui-dev; npm run build && npm run deploy

	docker build \
	  -t thomas-server:${TAG} \
	  -t mellesies/thomas-server:${TAG} \
	  ./

docker-run:
	# Run the docker image
	docker run --rm -it -p 5000:5000 thomas-server:${TAG}

docker-push:
	# Pushing the docker image
	mellesies/thomas-server:${TAG}

clean:
	# Cleaning ...
	-rm -r build
	-rm dist/*
