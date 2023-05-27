# test_examples.py

import pytest


class TestExamples:
    def test_blueprint_operands(self):
        from examples.blueprint_operands import main

        main()

    def test_filtered_train(self):
        from examples.filtered_train import main

        main()

    # def test_flip_belts(self):
    #     from examples.flip_belts import main
    #     main()

    def test_item_stack_signals(self):
        from examples.item_stack_signals import main

        main()

    # def test_pumpjack_placer(self): # TODO
    #     from examples.pumpjack_placer import main
    #     main()

    # def test_rail_planner_usage(self): # TODO
    #     from examples.rail_planner_usage import main
    #     main()

    def test_signal_index(self):
        from examples.signal_index import main

        main()

    def test_train_configuration(self):
        from examples.train_configuration_usage import main

        main()
