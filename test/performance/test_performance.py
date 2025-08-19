# test_performance.py

from draftsman import validators
from draftsman.blueprintable import get_blueprintable_from_string, BlueprintBook
from draftsman.constants import ValidationMode
from draftsman.warning import OverlappingObjectsWarning, UnknownElementWarning

import pytest
import warnings

validation_levels = (ValidationMode.DISABLED, ValidationMode.STRICT)

# @pytest.mark.benchmark()
# @pytest.mark.parametrize("validation_level", validation_levels)
# def test_import_huge_blueprint(benchmark, validation_level):
#     from test.performance.huge_blueprint_book import main

#     # This blueprint book includes things that a vanilla environment won't recognize;
#     # we intentionally ignore the warnings that they generate, as they're not
#     # really pertinent
#     # Ideally they would probably just be removed
#     warnings.filterwarnings("ignore", category=OverlappingObjectsWarning)
#     warnings.filterwarnings("ignore", category=UnknownElementWarning)

#     with validators.set_mode(validation_level):
#         book: BlueprintBook = benchmark(main)


@pytest.mark.benchmark()
@pytest.mark.parametrize("validation_level", validation_levels)
def test_set_section(benchmark, validation_level):
    from test.performance.set_section import main

    with validators.set_mode(validation_level):
        benchmark(main)


@pytest.mark.benchmark()
@pytest.mark.parametrize("validation_level", validation_levels)
def test_set_signal(benchmark, validation_level):
    from test.performance.set_signal import main

    with validators.set_mode(validation_level):
        benchmark(main)


@pytest.mark.benchmark()
@pytest.mark.parametrize("validation_level", validation_levels)
def test_add_entities(benchmark, validation_level):
    from test.performance.add_entities import main

    with validators.set_mode(validation_level):
        benchmark(main)


@pytest.mark.benchmark()
@pytest.mark.parametrize("validation_level", validation_levels)
def test_add_tiles(benchmark, validation_level):
    from test.performance.add_tiles import main

    with validators.set_mode(validation_level):
        benchmark(main)
