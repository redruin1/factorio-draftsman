# test_performance.py

from draftsman import validators
from draftsman.blueprintable import get_blueprintable_from_string, BlueprintBook
from draftsman.constants import ValidationMode
from draftsman.warning import UnknownElementWarning

import warnings

def test_import_export_big_blueprint(benchmark):
    # This blueprint book includes things that a vanilla environment won't recognize;
    # we intentionally ignore the warnings that they generate, as they're not
    # really pertinent
    # Ideally they would probably just be removed
    warnings.filterwarnings("ignore", category=UnknownElementWarning)

    # Import
    with open("test/performance/big_blueprint_book.txt") as file:
        book: BlueprintBook = benchmark(get_blueprintable_from_string(file.read()))

    # Export
    benchmark(book.to_string())

def test_import_export_big_blueprint_no_validation(benchmark):
    with validators.set_mode(ValidationMode.DISABLED):
        # Import
        with open("test/performance/big_blueprint_book.txt") as file:
            book: BlueprintBook = benchmark(get_blueprintable_from_string(file.read()))

        # Export
        benchmark(book.to_string())

def test_set_signal(benchmark):
    from test.performance.set_signal import main
    benchmark(main())