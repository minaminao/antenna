test:
	rm -rf ./archive
	python antenna.py --url_file url_sample.json
	python antenna.py --url_file url_sample.json