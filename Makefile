install:
	echo "hello"
dist:
	python -m build --sdist --wheel ./
