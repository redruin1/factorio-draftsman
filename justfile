set windows-shell := ["powershell.exe", "-c"]

pytest-args := "-Werror"

_no_target_provided:
    @just --list --unsorted

# Run 'lint + test + report-coverage'
ci: lint test report-coverage

# Run 'lint + test-all + report-coverage'
ci-all: lint test-all report-coverage

# Run black and ruff
lint *args:
    uv run black draftsman examples test
    uv run ruff check draftsman {{args}}

# Run test suite against {current Factorio version, all Python versions}
test: _test310 _test311 _test312 _test313

_test310:
    - uv run "--isolated" "--python=3.10" coverage run -p 

_test311:
    - uv run "--isolated" "--python=3.11" coverage run -p

_test312:
    - uv run "--isolated" "--python=3.12" coverage run -p 

_test313:
    - uv run "--isolated" "--python=3.13" coverage run -p


# Run test suite against {all Factorio versions, latest Python version} (LONG)
test-all: _giga-test313

# Ideally, we might want to run this test against all supported python versions,
# but that is a LOT of tests
_giga-test313:
    - uv run "--isolated" "--python=3.13" python test/test_all_factorio_versions.py

# Combine all coverage files and create HTML report
report-coverage:
    - uv run coverage combine
    uv run coverage html

# Run benchmark tests and save profiles for this Draftsman version
benchmark:
    - uv run pytest --benchmark-autosave test/performance
