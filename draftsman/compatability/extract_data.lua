-- extract_data.lua

-- TODO: fix entities
-- TODO: recipies
-- TODO: instruments

local function order_sort(a, b)
    --print(a.name, b.name)
    --print(a.order, b.order)
    local a_order = a.order or ""
    local b_order = b.order or ""
    if a_order == b_order then
        return a.name < b.name
    else
        return a_order < b_order
    end
    --return a.order < b.order or (a.order == b.order and a.name < b.name)
end

local function print_keys(t) 
    for k, v in pairs(t) do print(k, v) end
end

local function extract_entities()
    -- what we need:
    -- name: obviously
    -- enable_inventory_bar: determines if entity should have BarMixin (true by
    -- default)
    -- circuit_wire_max_distance: determines if circuit connectable
    -- filter_count: determines if filter inserter or normal inserter

    local entities = {}
    local entity_list = {}

    local with_filter = {}
    local with_inventory = {}
    local with_inventory_filter = {}
    local power_connectable = {}
    local circuit_connectable = {}
    local dual_circuit_connectable = {}
    local with_control_behavior = {}
    local not_rotatable = {}
    local placeable_off_grid = {}
    local building_direction_8_way = {}

    local entity_dimensions = {}
    local function get_dimensions(aabb)
        --print(serpent.block(selection_box))
        local x = math.floor((aabb[2][1] - aabb[1][1]) + 0.5)
        local y = math.floor((aabb[2][2] - aabb[1][2]) + 0.5)
        return x, y
    end

    local function categorize_entity(name, entity)
        print("\t", name)
        -- extract flags
        local flags = {}
        for _, flag in ipairs(entity.flags) do
            flags[flag] = true
        end
        print_keys(flags)
        if flags["not-blueprintable"] --[[or flags["hidden"]] then
            return
        end
        entity_list[#entity_list+1] = name
        if flags["not-rotatable"] then
            not_rotatable[#not_rotatable+1] = name
        end
        if flags["placeable-off-grid"] then
            placeable_off_grid[#placeable_off_grid+1] = name
        end
        if flags["building-direction-8-way"] then
            building_direction_8_way[#building_direction_8_way+1] = name
        end
        if entity.filter_count then
            with_filter[#with_filter+1] = name
        end
        if entity.maximum_wire_distance or entity.wire_max_distance then
            power_connectable[#power_connectable+1] = name
            circuit_connectable[#circuit_connectable+1] = name
        end
        if entity.circuit_wire_max_distance then
            circuit_connectable[#circuit_connectable+1] = name
        end
        if entity.input_connection_points and 
           entity.output_connection_points then
            dual_circuit_connectable[#dual_circuit_connectable+1] = name
        end
        print(serpent.block(entity.selection_box))
        entity_dimensions[name] = {get_dimensions(entity.selection_box)}
        entities[name] = entity
    end

    local function categorize_entities(list)
        for k, v in pairs(list) do
            categorize_entity(k, v)
        end
    end

    -- Chests
    -- TODO: narrow this category, includes a number of unplacable entities
    -- (crashed ship parts, factorio logos, etc.)
    categorize_entities(data.raw["container"])
    -- Storage tanks
    categorize_entities(data.raw["storage-tank"])
    -- Belts
    categorize_entities(data.raw["transport-belt"])
    categorize_entities(data.raw["underground-belt"])
    categorize_entities(data.raw["splitter"])
    -- Inserters
    categorize_entities(data.raw["inserter"])
    -- Loaders
    categorize_entities(data.raw["loader"])
    -- Electric poles
    categorize_entities(data.raw["electric-pole"])
    -- Pipes
    categorize_entities(data.raw["pipe"])
    categorize_entities(data.raw["pipe-to-ground"])
    -- Pumps
    categorize_entities(data.raw["pump"])
    -- Rails
    categorize_entities(data.raw["straight-rail"])
    categorize_entities(data.raw["curved-rail"])
    -- Train stops
    categorize_entities(data.raw["train-stop"])
    -- Rail signals
    categorize_entities(data.raw["rail-signal"])
    categorize_entities(data.raw["rail-chain-signal"])
    -- Train cars
    -- TODO: these are kinda special
    categorize_entities(data.raw["locomotive"])
    categorize_entities(data.raw["cargo-wagon"])
    categorize_entities(data.raw["fluid-wagon"])
    categorize_entities(data.raw["artillery-wagon"])
    -- Logistics containers
    categorize_entities(data.raw["logistic-container"])
    -- Roboports
    categorize_entities(data.raw["roboport"])
    -- Lamps
    categorize_entities(data.raw["lamp"])
    -- Combinators
    categorize_entities(data.raw["arithmetic-combinator"])
    categorize_entities(data.raw["decider-combinator"])
    categorize_entities(data.raw["constant-combinator"])
    categorize_entities(data.raw["power-switch"])
    categorize_entities(data.raw["programmable-speaker"])
    -- Boilers / Heat exchangers
    categorize_entities(data.raw["boiler"])
    -- Steam engines / turbines
    categorize_entities(data.raw["generator"])
    -- Solar panels
    categorize_entities(data.raw["solar-panel"])
    -- Accumulators
    categorize_entities(data.raw["accumulator"])
    -- Reactors
    categorize_entities(data.raw["reactor"])
    -- Heat pipes
    categorize_entities(data.raw["heat-pipe"])
    -- Mining drills (Burner, Electric, Pumpjack)
    categorize_entities(data.raw["mining-drill"])
    -- Offshore pumps
    categorize_entities(data.raw["offshore-pump"])
    -- Furnaces
    categorize_entities(data.raw["furnace"])
    -- Assembling machines (1-3 + chemical plant, refinery, and centrifuge)
    categorize_entities(data.raw["assembling-machine"])
    -- Labs
    categorize_entities(data.raw["lab"])
    -- Beacons
    categorize_entities(data.raw["beacon"])
    -- Rocket silos
    categorize_entities(data.raw["rocket-silo"])
    -- Landmines
    categorize_entities(data.raw["land-mine"])
    -- Walls
    categorize_entities(data.raw["wall"])
    -- Gates
    categorize_entities(data.raw["gate"])
    -- Turrets
    categorize_entities(data.raw["ammo-turret"])
    categorize_entities(data.raw["electric-turret"])
    categorize_entities(data.raw["artillery-turret"])
    -- Radars
    categorize_entities(data.raw["radar"])
    -- Electric Energy Interfaces
    categorize_entities(data.raw["electric-energy-interface"])
    -- Linked Containers
    categorize_entities(data.raw["linked-container"])
    -- Heat interfaces
    categorize_entities(data.raw["heat-interface"])
    -- Linked belts
    categorize_entities(data.raw["linked-belt"])
    -- Infinity containers
    categorize_entities(data.raw["infinity-container"])
    -- Infinity pipes
    categorize_entities(data.raw["infinity-pipe"])
    -- Burner generators
    categorize_entities(data.raw["burner-generator"])

    

    --print(serpent.block(entity_list))
    --print_keys(data.raw["container"])
    --print(serpent.block(data.raw["rocket-silo"]))

    local entities_file = io.open("draftsman/data/entities.py", "w")
    entities_file:write("# entities.py\n")
    entities_file:write("entity_dimensions = {\n")
    for i = 1, #entity_list do
        local entity = entity_list[i]
        local output_string = "    \"" .. entity .. "\": ("
        output_string = output_string .. entity_dimensions[entity][1] .. ", "
        output_string = output_string .. entity_dimensions[entity][2] .. "),\n"
        entities_file:write(output_string)
    end
    entities_file:write("}\n")
    entities_file:write("circuit_wire_distances = {\n")
    for i = 1, #circuit_connectable do
        local entity_name = circuit_connectable[i]
        local entity = entities[entity_name]
        local wire_dist = entity.circuit_wire_max_distance or entity.maximum_wire_distance or entity.wire_max_distance or 0
        entities_file:write("    \"" .. entity_name .. "\": " .. wire_dist .. ",\n")
    end
    entities_file:write("}\n")
    entities_file:write("power_wire_distances = {\n")
    for i = 1, #power_connectable do
        local entity_name = power_connectable[i]
        local entity = entities[entity_name]
        local wire_dist = entity.circuit_wire_max_distance or entity.maximum_wire_distance or entity.wire_max_distance or 0
        entities_file:write("    \"" .. entity_name .. "\": " .. wire_dist .. ",\n")
    end
    entities_file:write("}")
    entities_file:close()
end

local function extract_tiles()
    -- TODO: figure out some critera that determines whether a tile should be 
    -- placable or not by a blueprint; all related entries that I've found in
    -- data.raw have not been consistent.
    -- As a result, we load all tiles into tile_data.py regardless of whether or
    -- not they can actually be placed.
    -- In that case its left as an exercise of the blueprint maker to ensure
    -- they only use the correct tiles within them.

    local tiles = {}

    for k, v in pairs(data.raw["tile"]) do
        v.can_be_part_of_blueprint = v.can_be_part_of_blueprint == nil
        if v.can_be_part_of_blueprint then
            tiles[#tiles+1] = {name = k, order = v.order}
        end
    end

    -- Sort
    table.sort(tiles, order_sort)

    -- It might be better to write to a dict (or ordereddict) if we want to 
    -- preserve order for tiles like we do for signals.
    local tiles_file = io.open("draftsman/data/tiles.py", "w")
    tiles_file:write("# tiles.py\n")
    tiles_file:write("tile_names = {\n")
    for i = 1, #tiles do
        tiles_file:write("    \"" .. tiles[i].name .. "\",\n")
    end
    tiles_file:write("}")
    tiles_file:close()
end

local function extract_items()
    -- TODO?
end

local function extract_signals()
    -- TODO: maybe include more metadata for signals and their grouping
    -- Maybe make more fine control over which signals you want, like only 
    -- signals from a specific group? Need to find a use-case to justify the 
    -- work

    -- Item sort order: 
    -- (https://forums.factorio.com/viewtopic.php?p=23818#p23818)
    -- 1. item groups
    -- 2. item subgroups
    -- 3. item
    -- Across the previous categories, each is sorted by:
    -- 1. the item order string
    -- 2. the item name (lexographic)
    
    local groups = {}
    local index_dict = {}

    -- Initialize item groups
    for k, v in pairs(data.raw["item-group"]) do
        groups[#groups+1] = {name = v.name, order = v.order, subgroups = {}}
        index_dict[v.name] = groups[#groups]
    end

    -- Initialize Item subgroups
    for k, v in pairs(data.raw["item-subgroup"]) do
        local subgroups = index_dict[v.group].subgroups
        subgroups[#subgroups+1] = {name = v.name, order = v.order, group = v.group, items = {}}
        index_dict[v.name] = subgroups[#subgroups]
    end
    
    local function add_signal(category, name, type)
        --print(name)
        if name == "signal-unknown" or name == "fluid-unknown" or name == "item-unknown" then 
            return
        end
        local v = data.raw[category][name]
        
        if v.flags ~= nil then
            --print_keys(v.flags)
            for j = 1, #v.flags do
                if v.flags[j] == "hidden" then
                    --print(v.name .. " is hidden")
                    return
                end
            end
        end
        local subgroup = index_dict[v.subgroup or type]
        --print(v.subgroup)
        subgroup.items[#subgroup.items+1] = {name = v.name, type = type, order = v.order, subgroup = v.subgroup}
    end
    
    local function add_category(category, type)
        for name, _ in pairs(data.raw[category]) do
            add_signal(category, name, type)
        end
    end

    -- Load Item SignalIDs
    add_category("item", "item")                   -- regular items
    add_category("item-with-entity-data", "item")  -- cars, trains, etc.
    add_category("tool", "item")                   -- science packs
    add_category("ammo", "item")                   -- ammo types
    add_category("module", "item")                 -- module variants
    add_category("armor", "item")                  -- armor variants
    add_category("gun", "item")                    -- guns
    add_category("capsule", "item")                -- capsuloids
    -- Blueprint items
    add_signal("blueprint", "blueprint", "item")
    add_signal("blueprint-book", "blueprint-book", "item")
    add_signal("upgrade-item", "upgrade-planner", "item")
    add_signal("deconstruction-item", "deconstruction-planner", "item")
    -- Extras
    add_signal("spidertron-remote", "spidertron-remote", "item")
    add_signal("repair-tool", "repair-pack", "item") -- not an item somehow

    -- Rail signals are tricky
    -- The rail signal we see is in fact straight-rail by looking at debug ids,
    -- and curved-rail is also present if you look at the entities in the editor
    -- However, I cant seem to figure out what the flag/parameter is to show why
    -- straight-rail is shown in the inventory and curved-rail isnt, and where
    -- the name "rail" is stored in straight-rail's prototype.

    -- For now we manually add the item signal to save the headache for later
    item_name = "rail"
    item_order = "a[train-system]-a[rail]"
    item_subgroup = "train-transport"
    local subgroup = index_dict[item_subgroup]
    subgroup.items[#subgroup.items+1] = {name = item_name, type = "item", order = item_order, subgroup = item_subgroup}

    -- Fluid Signals
    add_category("fluid", "fluid")
    
    -- Virtual Signals
    add_category("virtual-signal", "virtual")

    -- Sort everything
    for i, v in ipairs(groups) do
        for j, v in ipairs(groups[i].subgroups) do
            table.sort(groups[i].subgroups[j].items, order_sort)
        end
        table.sort(groups[i].subgroups, order_sort)
    end
    table.sort(groups, order_sort)

    -- Flatten everything for output
    local signals = {} -- all signals
    local item_signals = {}
    local fluid_signals = {}
    local virtual_signals = {}

    local function categorize_signals(source, destination, type)
        for i, subgroup in ipairs(source.subgroups) do
            --print(i, subgroup.name)
            for j, item in ipairs(index_dict[subgroup.name].items) do
                --print("\t", j, item.name)
                signals[#signals+1] = {name = item.name, type = type}
                destination[#destination+1] = {name = item.name, type = type}
            end
        end
    end

    categorize_signals(index_dict["logistics"], item_signals, "item")
    categorize_signals(index_dict["production"], item_signals, "item")
    categorize_signals(index_dict["intermediate-products"], item_signals, "item")
    categorize_signals(index_dict["combat"], item_signals, "item")

    categorize_signals(index_dict["fluids"], fluid_signals, "fluid")

    categorize_signals(index_dict["signals"], virtual_signals, "virtual")

    -- if vanilla then assert #signals == 262 end

    -- Create a Python-readable data file with the signal data contents:
    local signals_file = io.open("draftsman/data/signals.py", "w")
    signals_file:write("# signals.py\n")
    signals_file:write("# Autogenerated with 'update_module.py'\n")
    --signals_file:write("from collections import OrderedDict")
    signals_file:write("from draftsman.signalID import SignalID\n")
    signals_file:write("signal_IDs = {\n")
    for i, v in ipairs(signals) do
        local output_string = ""
        output_string = "    \"" .. v.name .. "\": SignalID(\"" .. v.name
        output_string = output_string .. "\", \"" .. v.type .. "\"),\n"
        signals_file:write(output_string)
    end
    signals_file:write("}\n")

    signals_file:write("item_signals = {\n")
    for i, v in ipairs(item_signals) do
        local output_string = ""
        output_string = "    \"" .. v.name .. "\": signal_IDs[\"" .. v.name
        output_string = output_string .. "\"],\n"
        signals_file:write(output_string)
    end
    signals_file:write("}\n")

    signals_file:write("fluid_signals = {\n")
    for i, v in ipairs(fluid_signals) do
        local output_string = ""
        output_string = "    \"" .. v.name .. "\": signal_IDs[\"" .. v.name
        output_string = output_string .. "\"],\n"
        signals_file:write(output_string)
    end
    signals_file:write("}\n")

    signals_file:write("virtual_signals = {\n")
    for i, v in ipairs(virtual_signals) do
        local output_string = ""
        output_string = "    \"" .. v.name .. "\": signal_IDs[\"" .. v.name
        output_string = output_string .. "\"],\n"
        signals_file:write(output_string)
    end
    signals_file:write("}\n")
    signals_file:close()
end

local function extract_recipes()
    -- only needed for assembling machines and ordering
    -- similarly structured to signal groups

    local categories = {}
    local index_dict = {}

    -- Initialize recipe categories
    for k, v in pairs(data.raw["recipe-category"]) do
        categories[#categories+1] = {name = v.name, recipies = {}}
        index_dict[v.name] = categories[#categories]
    end

    -- Initialize recipies
    for k, v in pairs(data.raw["recipe"]) do
        local category = v.category or "crafting"
        local recipies = index_dict[category].recipies
        recipies[#recipies+1] = {name = v.name, order = v.order, subgroup = v.subgroup, category = category}
        --index_dict[v.name] = recipies[#recipies]
    end

    -- Sort everything
    -- TODO, this isnt quite right, we need to also sort by subgroup
    -- for i, v in ipairs(category) do
    --     -- for j, v in ipairs(category[i].subgroups) do
    --     --     table.sort(groups[i].subgroups[j].items, order_sort)
    --     -- end
    --     table.sort(category[i].recipies, order_sort)
    -- end
    -- table.sort(category, order_sort)

    -- Flatten
    local machines = {}
    for k, machine in pairs(data.raw["assembling-machine"]) do
        machines[machine.name] = {}
        --print(machine.name)
        local cur_machine = machines[machine.name]
        for i in ipairs(machine.crafting_categories) do
            local category_name = machine.crafting_categories[i]
            --print("\t", category_name)
            local category = index_dict[category_name]
            for j in pairs(category.recipies) do
                local recipe = category.recipies[j]
                --print("\t\t", recipe.name)
                cur_machine[#cur_machine+1] = recipe.name
            end
        end
    end

    --print(serpent.block(machines))

    local recipes_file = io.open("draftsman/data/recipes.py", "w")
    recipes_file:write("# recipes.py\n")
    recipes_file:write("# Autogenerated with 'update_module.py'\n")
    recipes_file:write("recipes = {\n")

    local indent = "    " -- 4
    for machine, list in pairs(machines) do
        --print(machine, list)
        recipes_file:write(indent .. "\"" .. machine .. "\": [\n")
        indent = "        " -- 8
        for i in ipairs(list) do
            local recipe = list[i]
            recipes_file:write(indent .. "\"" .. recipe .. "\",\n")
        end
        indent = "    " -- 4
        recipes_file:write(indent .. "],\n")
    end

    recipes_file:write("}")
    recipes_file:close()
end

local function extract_instruments()
    -- for k, v in pairs(data.raw["programmable-speaker"]) do
    --     print(k, serpent.block(v))
    -- end
    local instruments = data.raw["programmable-speaker"]["programmable-speaker"].instruments
    print(serpent.block(instruments))

    local instruments_file = io.open("draftsman/data/instruments.py", "w")
    instruments_file:write("# instruments.py\n")
    instruments_file:write("# Autogenerated with 'update_module.py'\n")
    instruments_file:write("instruments = {\n")
    for name, speaker in pairs(data.raw["programmable-speaker"]) do
        local indent = "    " -- 4
        instruments_file:write(indent .. "\"" .. name .. "\": {\n")
        for i, instrument in ipairs(speaker.instruments) do
            indent = "        " -- 8
            instruments_file:write(indent .. "\"" .. instrument.name .. "\": [\n")
            for j, note in ipairs(instrument.notes) do
                indent = "            " -- 12
                instruments_file:write(indent .. "\"" .. note.name .. "\",\n")
            end
            indent = "        " -- 8
        instruments_file:write(indent .. "],\n")
        end
        indent = "    " -- 4
        instruments_file:write(indent .. "},\n")
    end
    instruments_file:write("}")
    instruments_file:close()
end

local function main()
    -- ENTITIES
    --extract_entities()

    -- TILES
    --extract_tiles()

    -- SIGNALS
    --extract_signals()

    -- RECIPES
    extract_recipes()

    -- INSTRUMENTS
    extract_instruments()

    --print_keys(data.raw["recipe"])
    --print(serpent.block(data.raw["recipe"]["kovarex-enrichment-process"]))
end

main()