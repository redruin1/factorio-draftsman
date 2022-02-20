# test.py

"""
Blueprint of almost every entity with the majority of their component variations
tested. Originally used as a big testing script, now used for illustration.
"""

import factoriotools
from factoriotools.entity import Direction


def main():
    # TODO: chage this so that it just executes unittest.main()
    blueprint = factoriotools.Blueprint()

    wooden_chest = factoriotools.new_entity("wooden-chest")
    wooden_chest.set_grid_position(0, 0)
    blueprint.add_entity(wooden_chest, id = "wooden_chest")

    iron_chest = factoriotools.new_entity("iron-chest")
    iron_chest.set_grid_position(1, 0)
    iron_chest.set_bar_index(20)
    blueprint.add_entity(iron_chest, id = "iron_chest")

    steel_chest = factoriotools.new_entity("steel-chest")
    steel_chest.set_grid_position(2, 0)
    steel_chest.set_bar_index(1)
    blueprint.add_entity(steel_chest, id = "steel_chest")
    
    storage_tank = factoriotools.new_entity("storage-tank")
    storage_tank.set_grid_position(0, 1)
    blueprint.add_entity(storage_tank, id = "storage_tank")

    blueprint.add_circuit_connection("red", "wooden_chest", "iron_chest")
    blueprint.add_circuit_connection("red", "iron_chest", "steel_chest")
    blueprint.add_circuit_connection("red", "steel_chest", "storage_tank")

    transport_belt = factoriotools.new_entity("transport-belt")
    transport_belt.set_grid_position(0, 4)
    transport_belt.set_connect_to_logistic_network(True)
    transport_belt.set_logistic_condition("uranium-235", ">", 100)
    blueprint.add_entity(transport_belt)
    transport_belt.set_connect_to_logistic_network(False)
    transport_belt.remove_logistic_condition()
    transport_belt.set_grid_position(1, 4)
    transport_belt.set_enable_disable(False)
    transport_belt.set_read_hand_contents(True)
    transport_belt.set_read_mode(factoriotools.ReadMode.PULSE)
    blueprint.add_entity(transport_belt, id = "yellow_belt")

    #fast_belt = factoriotools.new_entity("fast-transport-belt")
    fast_belt = factoriotools.TransportBelt(name="fast-transport-belt")
    fast_belt.set_grid_position(2, 4)
    fast_belt.set_enable_disable(True)
    fast_belt.set_enabled_condition("electric-mining-drill", ">", 15)
    blueprint.add_entity(fast_belt, id = "red_belt")
    fast_belt.set_grid_position(3, 4)
    fast_belt.set_direction(Direction.WEST)
    fast_belt.set_enable_disable(True)
    fast_belt.set_read_hand_contents(True)
    fast_belt.set_read_mode(factoriotools.ReadMode.HOLD)
    fast_belt.set_enabled_condition() # Reset enabled condition
    print(fast_belt)
    blueprint.add_entity(fast_belt, id = "other_red_belt")
    #fast_belt.set_name("express-transport-belt")
    express_belt = factoriotools.TransportBelt(
        name="express-transport-belt", 
        position=[4, 4],
        direction = Direction.EAST,
        control_behavior={
            "circuit_enable_disable": True,
            "circuit_read_hand_contents": True,
            "circuit_contents_read_mode": 0,
            "circuit_condition": {
                "first_signal": "signal-blue",
                "comparator": ">=",
                "second_signal": "signal-blue"
            }
        })
    blueprint.add_entity(express_belt, id = "blue_belt")

    blueprint.add_circuit_connection("red", "yellow_belt", "red_belt")
    blueprint.add_circuit_connection("green", "other_red_belt", "blue_belt")

    underground_belt = factoriotools.new_entity("underground-belt")
    underground_belt.set_grid_position(0, 6)
    blueprint.add_entity(underground_belt)
    underground_belt.set_grid_position(0, 5)
    underground_belt.set_io_type("output")
    blueprint.add_entity(underground_belt)

    underground_belt = factoriotools.UndergroundBelt(name = "fast-underground-belt")
    underground_belt.set_grid_position(1, 5)
    underground_belt.set_io_type("output")
    blueprint.add_entity(underground_belt)
    underground_belt.set_grid_position(1, 6)
    underground_belt.set_io_type("input")
    blueprint.add_entity(underground_belt)

    underground_belt = factoriotools.new_entity("express-underground-belt")
    underground_belt.set_direction(Direction.EAST)
    blueprint.add_entity(underground_belt, id = "under1")
    blueprint.add_entity(underground_belt, id = "under2")

    blueprint.find_entity_by_id("under1").set_grid_position(2, 5)
    #blueprint.entities["under1"].set_io_type("input") # input is default
    blueprint.find_entity_by_id("under2").set_grid_position(3, 5)
    blueprint.find_entity_by_id("under2").set_io_type("output")

    splitter = factoriotools.Splitter("splitter")
    splitter.set_grid_position(0, 7)
    blueprint.add_entity(splitter)
    splitter.name = "fast-splitter"
    splitter.direction = Direction.SOUTH
    splitter.input_priority = "left"
    splitter.output_priority = "right"
    splitter.set_grid_position(2, 7)
    blueprint.add_entity(splitter)
    splitter.name = "express-splitter"
    splitter.set_direction(Direction.EAST)
    splitter.set_grid_position(4, 6) # currently busted with rotated entities
    #splitter.set_absolute_position(4.5, 7) # can do this instead
    splitter.set_input_priority(None)
    splitter.set_output_priority("left")
    splitter.set_filter("small-lamp")
    blueprint.add_entity(splitter)

    # Inserters
    inserter = factoriotools.Inserter("burner-inserter")
    inserter.set_direction(Direction.SOUTH)

    inserter.set_grid_position(0, 8)
    inserter.set_mode_of_operation(factoriotools.ModeOfOperation.NONE) # this is far too close to None
    inserter.set_stack_size_override(2)
    inserter.set_connect_to_logistic_network(True)
    inserter.set_logistic_condition("iron-plate", "<", 1000)
    blueprint.add_entity(inserter, id = "a")
    
    inserter.name = "inserter"
    inserter.set_grid_position(1, 8)
    inserter.set_connect_to_logistic_network(False)
    inserter.remove_logistic_condition()
    inserter.set_stack_size_override(None)
    inserter.set_mode_of_operation(None)
    inserter.set_enabled_condition("crude-oil", "=", "heavy-oil")
    blueprint.add_entity(inserter, id = "b")

    inserter.name = "long-handed-inserter"
    inserter.set_grid_position(2, 8)
    inserter.remove_enabled_condition()
    inserter.set_mode_of_operation(factoriotools.ModeOfOperation.NONE)
    inserter.set_read_hand_contents(True)
    inserter.set_read_mode(factoriotools.ReadMode.PULSE)
    blueprint.add_entity(inserter, id = "c")

    inserter.name = "fast-inserter"
    inserter.set_grid_position(3, 8)
    inserter.set_mode_of_operation(None)
    inserter.set_read_mode(factoriotools.ReadMode.HOLD)
    inserter.set_enabled_condition("signal-1", ">=", "signal-2")
    blueprint.add_entity(inserter, id = "d")

    inserter.name = "stack-inserter"
    inserter.set_grid_position(4, 8)
    inserter.set_enabled_condition("signal-anything", ">", 0)
    inserter.set_read_hand_contents(True)
    inserter.set_read_mode(factoriotools.ReadMode.PULSE)
    inserter.set_circuit_stack_size(True)
    inserter.set_stack_control_signal("signal-S")
    blueprint.add_entity(inserter, id = "e")

    blueprint.add_circuit_connection("green", "a", "b")
    blueprint.add_circuit_connection("green", "b", "c")
    blueprint.add_circuit_connection("green", "c", "d")
    blueprint.add_circuit_connection("green", "d", "e")

    # Filter inserters
    blueprint.add_entity("filter-inserter", position = [0, 9], id = "unwired1")
    blueprint.add_entity("stack-filter-inserter", position = [1, 9], id = "unwired2")

    filter_inserter = blueprint.find_entity_by_id("unwired1")
    filter_inserter.set_item_filters([
        "logistic-chest-active-provider", 
        "logistic-chest-passive-provider",
        "logistic-chest-storage",
        "logistic-chest-buffer",
        "logistic-chest-requester"
    ])
    stack_filter_inserter = blueprint.find_entity_by_id("unwired2")
    stack_filter_inserter.set_item_filters([
        "roboport"
    ])
    stack_filter_inserter.set_filter_mode("blacklist")
    stack_filter_inserter.set_stack_size_override(6)

    blueprint.add_entity(
        "filter-inserter", id = "wired1",
        position = [2, 9], 
        direction = Direction.SOUTH,
        control_behavior = {
            "circuit_mode_of_operation": factoriotools.ModeOfOperation.SET_FILTERS,
            "circuit_hand_read_mode": factoriotools.ReadMode.HOLD,
            "circuit_set_stack_size": True,
            "stack_control_input_signal": "signal-S"
        }
    )
    blueprint.add_entity(
        "stack-filter-inserter", id = "wired2",
        position = [3, 9],
        direction = Direction.SOUTH,
        control_behavior = {
            #"circuit_condition": ["signal-anything", ">", 10],
            "circuit_condition": {
                "first_signal": "signal-anything",
                "comparator": ">",
                "constant": 10
            },
            "circuit_read_hand_contents": True,
            "circuit_set_stack_size": True,
            "stack_control_input_signal": "signal-S"
        },
        filters = ["raw-fish"],
        filter_mode = "blacklist"
    )
    blueprint.add_circuit_connection("red", "wired1", "wired2")

    # Loaders
    blueprint.add_entity(
        "loader", 
        position = [0, 10],
        direction = Direction.NORTH,
        type = "output"
    )
    blueprint.add_entity(
        "fast-loader", 
        position = [1, 10],
        direction = Direction.SOUTH,
        filters = ["wood"],
        type = "input"
    )
    blueprint.add_entity(
        "express-loader", 
        position = [2, 10],
        direction = Direction.SOUTH,
        filters = ["coal", "stone", "iron-ore", "copper-ore", "uranium-ore"],
        type = "output"
    )

    wood_pole = factoriotools.ElectricPole("small-electric-pole")
    wood_pole.set_grid_position(0, 12)
    blueprint.add_entity(wood_pole, id = "wood_pole")
    medium_pole = factoriotools.ElectricPole("medium-electric-pole")
    medium_pole.set_grid_position(1, 12)
    #medium_pole.add_power_connection(wood_pole, "wood_pole") # duplicate, but lets handle
    #medium_pole.add_power_connection("big_pole")
    blueprint.add_entity(medium_pole, id = "medium_pole")
    blueprint.add_entity(
        "big-electric-pole", id = "big_pole",
        position = [2, 12],
        neighbours = ["medium_pole", "substation"]
    )
    blueprint.add_entity(
        "substation", id = "substation",
        position = [4, 12],
        neighbours = ["big_pole"]
    )

    blueprint.add_power_connection("wood_pole", "medium_pole")
    blueprint.add_power_connection("medium_pole", "wood_pole")
    blueprint.add_circuit_connection("red", "big_pole", "substation")
    blueprint.add_circuit_connection("green", "big_pole", "substation")

    blueprint.add_entity("pipe", position = [0, 14])
    blueprint.add_entity("pipe-to-ground", position = [1, 14], direction = Direction.WEST)
    blueprint.add_entity("pipe-to-ground", position = [2, 14], direction = Direction.EAST)

    pump = factoriotools.Pump("pump")
    pump.set_direction(Direction.EAST)
    pump.set_grid_position(3, 14)
    pump.set_enabled_condition("substation", ">", 1)
    blueprint.add_entity(pump, id = "pump")

    blueprint.add_circuit_connection("red", "substation", "pump")
    blueprint.add_circuit_connection("green", "substation", "pump")

    rail = factoriotools.StraightRail("straight-rail")
    rail.set_direction(Direction.EAST)
    sx, sy = 0, 16
    for y in range(4):
        for x in range(3):
            rail.set_grid_position(sx + x * 2, sy + y * 2)
            blueprint.add_entity(rail)

    train_stop = factoriotools.TrainStop("train-stop", position = [4, 24])
    train_stop.set_direction(Direction.EAST)
    train_stop.set_station_name("Luke Hoschke")
    train_stop.set_manual_trains_limit(1)
    # Train stop circuitry
    train_stop.set_enable_disable(True)
    train_stop.set_enabled_condition("express-transport-belt", ">", 100)
    train_stop.set_read_from_train(True)
    train_stop.set_read_stopped_train(True)
    train_stop.set_train_stopped_signal("signal-T")
    train_stop.set_trains_limit(True)
    train_stop.set_trains_limit_signal("signal-L")
    train_stop.set_read_trains_count(True)
    train_stop.set_trains_count_signal("signal-C")
    # train stop logistic condition
    train_stop.set_connect_to_logistic_network(True)
    train_stop.set_logistic_condition("locomotive", ">", 10)
    blueprint.add_entity(train_stop, id = "train_stop")

    rail_signal = factoriotools.RailSignal("rail-signal", position = [3, 15])
    rail_signal.set_direction(Direction.EAST)
    rail_signal.set_enable_disable(True)
    rail_signal.set_enabled_condition("signal-check", "=", 0)
    rail_signal.set_read_signal(True)
    blueprint.add_entity(rail_signal, id = "circuit_rail")
    rail_signal.set_grid_position(2, 24)
    rail_signal.set_direction(Direction.WEST)
    rail_signal.set_enable_disable(None)
    rail_signal.remove_enabled_condition()
    rail_signal.set_read_signal(None)
    blueprint.add_entity(rail_signal)

    blueprint.add_circuit_connection("red", "circuit_rail", "pump")

    chain_signal = factoriotools.RailChainSignal("rail-chain-signal")
    chain_signal.set_grid_position(0, 15)
    chain_signal.set_direction(Direction.EAST)
    chain_signal.set_blue_output_signal("signal-B")
    blueprint.add_entity(chain_signal, id = "circuit_chain")
    chain_signal.set_grid_position(0, 24)
    chain_signal.set_direction(Direction.WEST)
    chain_signal.set_blue_output_signal(None) # Reset to default
    blueprint.add_entity(chain_signal)

    blueprint.add_circuit_connection("green", "circuit_chain", "pump")

    blueprint.add_entity("locomotive", position = {"x":3, "y":17}, orientation = 0.25)
    blueprint.add_entity("cargo-wagon", position = {"x":3, "y":19}, orientation = 0.25, id = "wagon")
    blueprint.add_entity("fluid-wagon", position = {"x":3, "y":21}, orientation = 0.25)
    blueprint.add_entity("artillery-wagon", position = {"x":3, "y":23}, orientation = 0.25)

    wagon = blueprint.find_entity_by_id("wagon")
    wagon.set_inventory_filter(0, "transport-belt")
    wagon.set_inventory_filter(11, "fast-transport-belt")
    wagon.set_inventory_filter(22, "express-transport-belt")
    wagon.set_inventory_filter(33, "logistic-robot")
    wagon.set_bar_index(34)

    blueprint.add_entity("logistic-chest-active-provider", position = [0, 25])
    blueprint.add_entity("logistic-chest-passive-provider", position = [1, 25])

    storage = factoriotools.LogisticStorageContainer("logistic-chest-storage")
    storage.set_grid_position(2, 25)
    storage.set_request_filter(0, "light-oil-barrel")
    blueprint.add_entity(storage)
    buffer = factoriotools.LogisticBufferContainer("logistic-chest-buffer")
    buffer.set_grid_position(3, 25)
    buffer.set_request_filters([("electronic-circuit", 200), ("advanced-circuit", 200)])
    blueprint.add_entity(buffer)
    requester = factoriotools.LogisticRequestContainer("logistic-chest-requester")
    requester.set_grid_position(4, 26)
    requester.set_mode_of_operation(factoriotools.ModeOfOperation.SET_FILTERS)
    requester.set_request_from_buffers(True)
    blueprint.add_entity(requester, id = "requester")

    roboport = factoriotools.Roboport("roboport", position = [0, 26])
    roboport.set_read_logistics(True)
    roboport.set_read_robot_stats(True)
    roboport.set_available_logistics_signal("signal-A")
    roboport.set_total_logistics_signal("signal-B")
    roboport.set_available_construction_signal("signal-C")
    roboport.set_total_construction_signal("signal-D")
    blueprint.add_entity(roboport, id = "roboport")

    lamp = factoriotools.Lamp("small-lamp", position = [5, 26])
    lamp.set_enabled_condition("signal-A", ">", 0)
    lamp.set_use_colors(True)
    #lamp.set_enable_disable(True) # error!
    blueprint.add_entity(lamp, id = "lamp")

    arithmetic = factoriotools.ArithmeticCombinator("arithmetic-combinator")
    arithmetic.set_grid_position(4, 27)
    arithmetic.set_arithmetic_conditions("signal-A", "+", 10, "signal-A")
    blueprint.add_entity(arithmetic, id = "arithmetic")
    print(arithmetic)

    decider = factoriotools.DeciderCombinator("decider-combinator")
    decider.set_grid_position(5, 27)
    decider.set_decider_conditions("signal-A", ">", 0, "signal-red")
    decider.set_copy_count_from_input(False)
    blueprint.add_entity(decider, id = "decider")

    constant = factoriotools.ConstantCombinator("constant-combinator")
    constant.set_grid_position(5, 29)
    constant.set_signal(0, "signal-A", 1)
    blueprint.add_entity(constant, id = "constant")

    blueprint.add_circuit_connection("red", "train_stop", "requester")
    blueprint.add_circuit_connection("red", "requester", "roboport")
    blueprint.add_circuit_connection("red", "requester", "lamp")
    blueprint.add_circuit_connection("green", "constant", "decider")
    blueprint.add_circuit_connection("green", "decider", "arithmetic")
    blueprint.add_circuit_connection("green", "arithmetic", "decider", 2, 2)
    blueprint.add_circuit_connection("green", "decider", "lamp", 2, 1)

    power_switch = factoriotools.PowerSwitch("power-switch")
    power_switch.set_grid_position(0, 30)
    power_switch.set_enabled_condition("iron-ore", ">", 0)
    power_switch.set_connect_to_logistic_network(True)
    power_switch.set_logistic_condition("wood", ">", 100)
    blueprint.add_entity(power_switch, id = "ps1")
    power_switch.set_grid_position(2, 30)
    power_switch.remove_enabled_condition()
    power_switch.set_connect_to_logistic_network(None)
    power_switch.remove_logistic_condition()
    power_switch.set_switch_state(True)
    blueprint.add_entity(power_switch, id = "ps2")
    blueprint.add_entity("substation", id = "lower_substation", position = [4, 30])

    blueprint.add_power_connection("substation", "lower_substation")

    blueprint.add_circuit_connection("red", "ps1", "lower_substation")
    blueprint.add_power_connection("ps1", "lower_substation", 1, 1)
    blueprint.add_power_connection("ps1", "lower_substation", 2, 1)
    blueprint.add_power_connection("ps2", "lower_substation", 1, 1)
    blueprint.add_power_connection("ps2", "lower_substation", 2, 1)

    speaker = factoriotools.ProgrammableSpeaker("programmable-speaker")
    speaker.set_grid_position(0, 32)
    speaker.set_global_playback(True)
    speaker.set_show_alert(True)
    speaker.set_polyphony(True)
    speaker.set_alert_icon("signal-check")
    speaker.set_alert_message("Big warning [virtual-signal=signal-check]")
    speaker.set_show_alert_on_map(True)
    blueprint.add_entity(speaker)
    
    speaker = factoriotools.ProgrammableSpeaker("programmable-speaker")
    speaker.set_grid_position(1, 32)
    speaker.set_polyphony(True)
    speaker.set_enabled_condition("signal-red", ">", 0)
    speaker.set_instrument(1)
    speaker.set_instrument(0)
    blueprint.add_entity(speaker, id = "speaker2")
    blueprint.add_circuit_connection("red", "speaker2", "lower_substation")

    speaker = factoriotools.ProgrammableSpeaker("programmable-speaker")
    speaker.set_grid_position(2, 32)
    speaker.set_volume(0.5)
    speaker.set_instrument(3)
    speaker.set_enabled_condition("signal-P")
    speaker.set_signal_value_is_pitch(True)
    blueprint.add_entity(speaker, id = "speaker3")
    blueprint.add_circuit_connection("red", "speaker3", "lower_substation")

    blueprint.add_tile("stone-path", 0, 32)
    blueprint.add_tile("concrete", 1, 32)
    blueprint.add_tile("hazard-concrete-left", 2, 32)
    blueprint.add_tile("refined-concrete", 3, 32)
    blueprint.add_tile("refined-hazard-concrete-left", 4, 32)
    blueprint.add_tile("landfill", 5, 32)

    blueprint.add_entity("boiler", position = [0, 33])
    blueprint.add_entity("heat-exchanger", position = [3, 32], direction = Direction.WEST)

    blueprint.add_entity("steam-engine", position = [0, 35])
    blueprint.add_entity("steam-turbine", position = [3, 35])

    blueprint.add_entity("solar-panel", position = [0, 40])

    accumulator = factoriotools.Accumulator("accumulator", position = [3, 40])
    accumulator.set_output_signal("signal-A")
    blueprint.add_entity(accumulator, id = "accumulator")
    blueprint.add_entity("substation", id = "bottom_substation", position = [4, 48])
    
    blueprint.add_power_connection("lower_substation", "bottom_substation")
    blueprint.add_circuit_connection("red", "accumulator", "bottom_substation")

    blueprint.add_entity("nuclear-reactor", position = [0, 43])

    blueprint.add_entity("heat-pipe", position = [4, 42])

    burner_miner = factoriotools.MiningDrill("burner-mining-drill")
    burner_miner.set_grid_position(0, 48)
    burner_miner.set_direction(Direction.SOUTH)
    burner_miner.set_enable_disable(True)
    burner_miner.set_enabled_condition("crude-oil", ">", 0)
    blueprint.add_entity(burner_miner, id = "burner_miner_1")
    burner_miner.set_grid_position(2, 48)
    burner_miner.set_enable_disable(False)
    burner_miner.remove_enabled_condition()
    burner_miner.set_read_resources(True)
    burner_miner.set_read_mode(1) # ENTIRE_PATCH
    blueprint.add_entity(burner_miner, id = "burner_miner_2")

    electric_miner = factoriotools.MiningDrill("electric-mining-drill")
    electric_miner.set_grid_position(0, 50)
    #electric_miner.set_direction(Direction.NORTH) # default
    electric_miner.set_enable_disable(False)
    electric_miner.set_read_resources(True)
    electric_miner.set_read_mode(0) # THIS_MINER
    electric_miner.set_connect_to_logistic_network(True)
    electric_miner.set_logistic_condition("copper-ore", "<", 1000)
    electric_miner.set_item_request("productivity-module-3", 3)
    blueprint.add_entity(electric_miner, id = "electric_miner")

    pumpjack = factoriotools.MiningDrill("pumpjack")
    pumpjack.set_grid_position(3, 50)
    pumpjack.set_direction(Direction.EAST)
    pumpjack.set_enable_disable(False)
    pumpjack.set_read_resources(True)
    #pumpjack.set_read_mode(0) # Pumpjacks shouldnt have this method but im too lazy to fix right now
    pumpjack.set_item_requests({"speed-module-3": 2}) # TODO: warnings
    blueprint.add_entity(pumpjack, id = "pumpjack")

    blueprint.add_circuit_connection("red", "burner_miner_1", "burner_miner_2")
    blueprint.add_circuit_connection("red", "burner_miner_2", "bottom_substation")
    blueprint.add_circuit_connection("red", "burner_miner_1", "electric_miner")
    blueprint.add_circuit_connection("red", "electric_miner", "pumpjack")

    furnace = factoriotools.Furnace("stone-furnace")
    furnace.set_grid_position(0, 53)
    blueprint.add_entity(furnace)
    furnace.name = "steel-furnace"
    furnace.set_grid_position(2, 53)
    blueprint.add_entity(furnace)
    furnace.name = "electric-furnace"
    furnace.set_grid_position(4, 53)
    furnace.set_item_request("effectivity-module-3", 2)
    blueprint.add_entity(furnace)

    assembling_machine = factoriotools.AssemblingMachine("assembling-machine-1")
    assembling_machine.set_grid_position(0, 56)
    assembling_machine.set_recipe("iron-gear-wheel")
    blueprint.add_entity(assembling_machine)
    assembling_machine.name = "assembling-machine-3"
    assembling_machine.set_grid_position(3, 56)
    assembling_machine.set_recipe("utility-science-pack")
    assembling_machine.set_item_requests({
        "speed-module": 1, 
        "productivity-module": 1, 
        "effectivity-module": 1
    })
    blueprint.add_entity(assembling_machine)

    # ==========================================================

    blueprint.set_icons("signal-T", "signal-E", "signal-S", "signal-T")
    blueprint.set_label("Almost Everything")

    # for y in range(5):
    #     for x in range(5):
    #         if (x + y) % 2 == 0:
    #             land_mine = factoriotools.LandMine("land-mine", position=[x, y])
    #             blueprint.add_entity(land_mine)

    # blueprint.add_entity("gate", direction = Direction.EAST)
    # wall = factoriotools.Wall("stone-wall", position = [-1, 0])
    # wall.set_enable_disable(True)
    # wall.set_enabled_condition("signal-anything", ">", 0)
    # wall.set_read_gate(True)
    # wall.set_output_signal("signal-0")
    # blueprint.add_entity(wall, id = "left_wall")
    # wall = factoriotools.Wall("stone-wall", position = [1, 0])
    # wall.set_enable_disable(False)
    # wall.set_read_gate(True)
    # wall.set_output_signal("signal-red")
    # blueprint.add_entity(wall, id = "right_wall")

    # blueprint.add_entity("medium-electric-pole", position = [-3, 0], id = "lp")
    # blueprint.add_entity("medium-electric-pole", position = [ 3, 0], id = "rp")
    
    # blueprint.add_circuit_connection("red", "lp", "left_wall")
    # blueprint.add_circuit_connection("green", "rp", "right_wall")
    
    print(blueprint)
    print(blueprint.to_string())


if __name__ == "__main__":
    main()