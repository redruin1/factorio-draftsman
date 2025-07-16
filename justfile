set shell := ["uv", "run"]
set windows-shell := ["powershell.exe", "-c", "uv", "run"]

pytest-args := "-Werror"

ci: lint test report-coverage

lint *args:
    black draftsman examples test
    ruff check draftsman {{args}}

test: test310 test311 test312 test313

test310 *args:
    - "--isolated" "--python=3.10" coverage run -p --omit "examples/**" -m pytest test {{pytest-args}} {{args}}

test311 *args:
    - "--isolated" "--python=3.11" coverage run -p --omit "examples/**" -m pytest test {{pytest-args}} {{args}}

test312 *args:
    - "--isolated" "--python=3.12" coverage run -p --omit "examples/**" -m pytest test {{pytest-args}} {{args}}

test313 *args:
    - "--isolated" "--python=3.13" coverage run -p --omit "examples/**" -m pytest test {{pytest-args}} {{args}}

report-coverage:
    -coverage combine
    coverage report
    coverage html
