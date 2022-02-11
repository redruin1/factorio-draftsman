-- extract_data.lua

-- TODO: do entities
-- TODO: recipies
-- TODO: maybe order signals using their factorio ordering system? might be nice

local function add_signal(signals, name, type)
    signals[#signals+1] = {name = name, type =  type, order = order}
end


local function add_dict(signals, dict, type)
    local count = 0
    for k, v in pairs(data.raw[dict]) do
        print(k, v.order)
        if v.flags ~= nil then
            for j = 1, #v.flags do
                if v.flags[j] == "hidden" then
                    --print(v.name .. " is hidden")
                    goto continue
                end
            end
        end
        if k == "signal-unknown" or k == "fluid-unknown" then goto continue end
        signals[#signals+1] = {name = k, type = type, order = v.order}
        ::continue::
    end
    --print(count .. " signals in " .. dict)
end

local function scrape_tiles(tiles, dict)
    for k, v in pairs(data.raw[dict]) do
        if v.place_as_tile ~= nil then
            print(k)
        end
    end
end


local function compare_difference(signals, should_have)
    for i = 1, #should_have do
        --print(should_have[i])
        local entry = should_have[i]
        if not signals[entry] then
            print("Should have " .. entry)
        end
    end
end

local function order_sort(a, b)
    return a.order < b.order
end

local function print_keys(t) 
    for k, v in pairs(t) do print(k, v) end
end

local function extract_entities()
    --[[ Load Entities ]]

    -- what we need:
    -- name: obviously
    -- enable_inventory_bar: determines if entity should have BarMixin (true by
    -- default)
    -- circuit_wire_max_distance: determines if circuit connectable
    -- filter_count: determines if filter inserter or normal inserter

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
        local x = math.floor(aabb[2][1] - aabb[1][1]) + 1
        local y = math.floor(aabb[2][2] - aabb[1][2]) + 1
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
        if flags["not-blueprintable"] or flags["hidden"] then
            return
        end
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
        if entity.maximum_wire_distance then
            power_connectable[#power_connectable+1] = name
        end
        if entity.circuit_wire_max_distance then
            circuit_connectable[#circuit_connectable+1] = name
        end
        if entity.input_connection_points and 
           entity.output_connection_points then
            dual_circuit_connectable[#dual_circuit_connectable+1] = name
        end
        entity_dimensions[name] = get_dimensions(entity.collision_box)
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
    -- Radars
    categorize_entities(data.raw["radar"])

    print(serpent.block(entity_dimensions))
    print_keys(data.raw["rocket-silo"])
    print_keys(data.raw["container"])
    --print(serpent.block(data.raw["rocket-silo"]))

end

local function extract_tiles()
    --[[ Load Tiles ]]

    -- We're gonna load all tiles regardless of anything
    -- This means that potentially valid blueprints will be constructed with
    -- tiles that cannot be placed within a blueprint
    -- In that case its left as an exercise of the blueprint maker to ensure
    -- they only use the correct tiles within them

    local tiles = {}

    for k, v in pairs(data.raw["tile"]) do
        v.can_be_part_of_blueprint = v.can_be_part_of_blueprint == nil
        if v.can_be_part_of_blueprint then
            tiles[#tiles+1] = {name = k, order = v.order}
        end
    end

    table.sort(tiles, order_sort)

    local tiles_file = io.open("factoriotools/tile_data.py", "w")
    tiles_file:write("# tile_data.py\n")
    tiles_file:write("tile_names = {\n")
    for i = 1, #tiles do
        tiles_file:write("\t\"" .. tiles[i].name .. "\",\n")
    end
    tiles_file:write("}")
    tiles_file:close()
end

local function extract_recipes()
    -- only needed for assembling machines and ordering
end


local function main()
    -- ENTITIES
    extract_entities()

    -- TILES
    --extract_tiles()


    -- WRITE FILES
    --[=[

    --[[ Load Signals ]]

    local signals = {}
    local item_signals = {}
    local fluid_signals = {}
    local virtual_signals = {}
    -- Load Item SignalIDs
    add_dict(signals, "item", "item")                   -- regular items
    add_dict(signals, "item-with-entity-data", "item")  -- cars, trains, etc.
    add_dict(signals, "tool", "item")                   -- science packs
    add_dict(signals, "ammo", "item")                   -- ammo types
    add_dict(signals, "module", "item")                 -- module variants
    add_dict(signals, "armor", "item")                  -- armor variants
    add_dict(signals, "gun", "item")                    -- guns
    add_dict(signals, "capsule", "item")                -- capsuloids
    -- Blueprint items
    add_signal(signals, "blueprint", "item")
    add_signal(signals, "blueprint-book", "item")
    add_signal(signals, "upgrade-planner", "item")
    add_signal(signals, "deconstruction-planner", "item")
    -- Extras
    add_signal(signals, "rail", "item")                 -- general rail signal
    add_signal(signals, "spidertron-remote", "item")    -- not a capsule somehow
    add_signal(signals, "repair-pack", "item")          -- not an item somehow

    for k, v in pairs(signals) do
        item_signals[#item_signals+1] = v.name
    end

    -- Load Fluid SignalIDs
    add_dict(signals, "fluid", "fluid")
    for k, _ in pairs(data.raw["fluid"]) do
        fluid_signals[#fluid_signals+1] = k
    end
    -- Load Virtual SignalIDs
    add_dict(signals, "virtual-signal", "virtual")
    for k, _ in pairs(data.raw["virtual-signal"]) do
        if k ~= "signal-unknown" then
            virtual_signals[#virtual_signals+1] = k
        end
    end

    --compare_difference(signals, should_have)

    -- sort the signals
    local function compare(a, b)
        print(a.name, b.name)
        print(a.order, b.order)
        return a.order < b.order
    end

    --local signal_list = {}
    --for k, v in pairs(signals) do table.insert(signal_list, v) end
    table.sort(signals, compare)

    --[[ Create a Python-readable data file with the signal data contents: ]]
    local signals_file = io.open("factoriotools/signal_data.py", "w")
    signals_file:write("# signal_data.py\n")
    signals_file:write("# Autogenerated with 'update_data.lua'\n")
    signals_file:write("from factoriotools.signalID import SignalID\n") -- this is way better
    signals_file:write("signal_IDs = {\n")
    for k, v in pairs(signals) do
        local output_string = ""
        output_string = "    \"" .. v.name .. "\": SignalID(\"" .. v.name
        output_string = output_string .. "\", \"" .. v.type .. "\"),\n"
        signals_file:write(output_string)
    end
    signals_file:write("}\n")

    signals_file:write("item_signals = {\n")
    for i, v in ipairs(item_signals) do
        --print(i, v)
        signals_file:write("\t\"" .. v .. "\",\n")
    end
    signals_file:write("}\n")

    signals_file:write("fluid_signals = {\n")
    for i, v in ipairs(fluid_signals) do
        --print(i, v)
        signals_file:write("\t\"" .. v .. "\",\n")
    end
    signals_file:write("}\n")

    signals_file:write("virtual_signals = {\n")
    for i, v in ipairs(virtual_signals) do
        --print(i, v)
        signals_file:write("\t\"" .. v .. "\",\n")
    end
    signals_file:write("}\n")
    signals_file:close()
    ]=]
end

main()