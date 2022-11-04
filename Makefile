test-sample:
	rm -rf ./archive
	python antenna.py --task-file task_sample.json
	python antenna.py --task-file task_sample.json

test:
	rm -rf ./archive
	python antenna.py
	python antenna.py

clean:
	rm -rf ./archive