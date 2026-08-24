# Local developer shortcuts for TradeTide's CMake and Python workflows.
# Override defaults as needed, for example: make PYTHON=python3.13 quick
PYTHON ?= .venv/bin/python
BUILD_DIR ?= build
ROOT_DIR := $(CURDIR)
PYBIND11_DIR := $(shell $(PYTHON) -m pybind11 --cmakedir)

.PHONY: bootstrap configure build install uninstall quick rebuild editable quality test clean

bootstrap:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install --upgrade "scikit-build-core>=0.3.3" pybind11 "setuptools_scm[toml]>=8.0"

quality:
	$(PYTHON) -m ruff check TradeTide tests
	$(PYTHON) -m mypy TradeTide/execution.py TradeTide/performance.py TradeTide/validation.py

test:
	MPLBACKEND=Agg $(PYTHON) -m pytest --config-file=pytest.ini

configure:
	cmake -S . -B $(BUILD_DIR) \
		-Dpybind11_DIR="$(PYBIND11_DIR)" \
		-DPython_EXECUTABLE="$$(which $(PYTHON))" \
		-DCMAKE_INSTALL_PREFIX="$(ROOT_DIR)"

build:
	cmake --build $(BUILD_DIR) -j

install:
	cmake --install $(BUILD_DIR)

uninstall:
	$(PYTHON) -m pip uninstall -y TradeTide

quick: configure build install

rebuild: configure build install

editable: bootstrap
	$(PYTHON) -m pip install --no-build-isolation -Cbuild-dir=$(BUILD_DIR) -Ceditable.rebuild=false -Ceditable.mode=inplace -e .

clean:
	@echo "Removing TradeTide build products"
	rm -rf $(BUILD_DIR) .skbuild
	rm -f TradeTide/*.so TradeTide/*.a
	rm -f TradeTide/binary/*.so TradeTide/binary/*.a
	rm -rf .pytest_cache htmlcov .coverage
