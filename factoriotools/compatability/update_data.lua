-- update_data.lua

-- TODO: do entities
-- TODO: handle mods
-- TODO: maybe order signals using their factorio ordering system? might be nice

local serpent = require("factoriotools.serpent")

-- Updates all data according to
--[[
should_have = {
    "signal-0", "signal-1", "signal-2", "signal-3", 
    "signal-4", "signal-5", "signal-6", "signal-7", 
    "signal-8", "signal-9", "signal-A", "signal-B", 
    "signal-C", "signal-D", "signal-E", "signal-F", 
    "signal-G", "signal-H", "signal-I", "signal-J", 
    "signal-K", "signal-L", "signal-M", "signal-N", 
    "signal-O", "signal-P", "signal-Q", "signal-R", 
    "signal-S", "signal-T", "signal-U", "signal-V",
    -- 32
    "signal-W", "signal-X", "signal-Y", "signal-Z", 
    "signal-check", "signal-dot", "signal-red", "signal-green", 
    "signal-blue", "signal-yellow", "signal-pink", "signal-cyan",
    "signal-white", "signal-grey", "signal-black", "signal-everything",
    "signal-anything", "signal-each", "signal-info",
    
    "wooden-chest", "red-wire", "green-wire",
    "iron-chest", "steel-chest", "storage-tank", "transport-belt",
    "fast-transport-belt", "express-transport-belt", "underground-belt", "fast-underground-belt",
    "express-underground-belt", "splitter", "fast-splitter", "express-splitter",
    "burner-inserter", "inserter", "long-handed-inserter", "fast-inserter",             
    -- 64
    "filter-inserter", "stack-inserter", "stack-filter-inserter", "small-electric-pole",
    "medium-electric-pole", "big-electric-pole", "substation", "pipe",
    "pipe-to-ground", "pump", "rail", "train-stop",
    "rail-signal", "rail-chain-signal", "locomotive", "cargo-wagon",
    "fluid-wagon", "artillery-wagon", "car", "tank",
    "spidertron", "spidertron-remote", "logistic-robot", "construction-robot",
    "logistic-chest-active-provider", "logistic-chest-passive-provider", "logistic-chest-storage", "logistic-chest-buffer",
    "logistic-chest-requester", "roboport", "small-lamp", "arithmetic-combinator",     
    -- 96
    "decider-combinator", "constant-combinator", "power-switch", "programmable-speaker",
    "stone-brick", "concrete", "hazard-concrete", "refined-concrete",
    "refined-hazard-concrete", "landfill", "cliff-explosives", "repair-pack",
    "blueprint", "deconstruction-planner", "upgrade-planner", "blueprint-book",
    "boiler", "steam-engine", "solar-panel", "accumulator",
    "nuclear-reactor", "heat-pipe", "heat-exchanger", "steam-turbine",
    "burner-mining-drill", "electric-mining-drill", "offshore-pump", "pumpjack",
    "stone-furnace", "steel-furnace", "electric-furnace", "assembling-machine-1", 
    -- 128
    "assembling-machine-2", "assembling-machine-3", "oil-refinery", "chemical-plant",
    "centrifuge", "lab", "beacon", "speed-module",
    "speed-module-2", "speed-module-3", "effectivity-module", "effectivity-module-2",
    "effectivity-module-3", "productivity-module", "productivity-module-2", "productivity-module-3",
    "rocket-silo", "satellite", "wood", "coal",
    "stone", "iron-ore", "copper-ore", "uranium-ore",
    "raw-fish", "iron-plate", "copper-plate", "solid-fuel",
    "steel-plate", "plastic-bar", "sulfur", "battery",
    -- 160
    "explosives", "crude-oil-barrel", "heavy-oil-barrel", "light-oil-barrel",
    "lubricant-barrel", "petroleum-gas-barrel", "sulfuric-acid-barrel", "water-barrel",
    "copper-cable", "iron-stick", "iron-gear-wheel", "empty-barrel",
    "electronic-circuit", "advanced-circuit", "processing-unit", "engine-unit",
    "electric-engine-unit", "flying-robot-frame", "rocket-control-unit", "low-density-structure",
    "rocket-fuel", "nuclear-fuel", "uranium-235", "uranium-238",
    "uranium-fuel-cell", "used-up-uranium-fuel-cell", "automation-science-pack", "logistic-science-pack",
    "military-science-pack", "chemical-science-pack", "production-science-pack", "utility-science-pack",
    -- 192
    "space-science-pack", "pistol", "submachine-gun", "shotgun",
    "combat-shotgun", "rocket-launcher", "flamethrower", "land-mine",
    "firearm-magazine", "piercing-rounds-magazine", "uranium-rounds-magazine", "shotgun-shell",
    "piercing-shotgun-shell", "cannon-shell", "explosive-cannon-shell", "uranium-cannon-shell",
    "explosive-uranium-cannon-shell", "artillery-shell", "rocket", "explosive-rocket",
    "atomic-bomb", "flamethrower-ammo", "grenade", "cluster-grenade",
    "poison-capsule", "slowdown-capsule", "defender-capsule", "distractor-capsule",
    "destroyer-capsule", "light-armor", "heavy-armor", "modular-armor",
    -- 224
    "power-armor", "power-armor-mk2", "solar-panel-equipment", "fusion-reactor-equipment",
    "battery-equipment", "battery-mk2-equipment", "belt-immunity-equipment", "exoskeleton-equipment",
    "personal-roboport-equipment", "personal-roboport-mk2-equipment", "night-vision-equipment", "energy-shield-equipment",
    "energy-shield-mk2-equipment", "personal-laser-defense-equipment", "discharge-defense-equipment", "discharge-defense-remote",
    "stone-wall", "gate", "gun-turret", "laser-turret",
    "flamethrower-turret", "artillery-turret", "artillery-targeting-remote", "radar",
    "water", "crude-oil", "steam", "heavy-oil",
    "light-oil", "petroleum-gas", "sulfuric-acid", "lubricant",
    -- 256
}
]]

local menu_simulations = {}
menu_simulations.forest_fire = {}
menu_simulations.solar_power_construction = {}
menu_simulations.lab = {}
menu_simulations.burner_city = {}
menu_simulations.mining_defense = {}
menu_simulations.biter_base_steamrolled = {}
menu_simulations.biter_base_spidertron = {}
menu_simulations.biter_base_artillery = {}
menu_simulations.biter_base_player_attack = {}
menu_simulations.biter_base_laser_defense = {}
menu_simulations.artillery = {}
menu_simulations.train_junction = {}
menu_simulations.oil_pumpjacks = {}
menu_simulations.oil_refinery = {}
menu_simulations.early_smelting = {}
menu_simulations.train_station = {}
menu_simulations.logistic_robots = {}
menu_simulations.nuclear_power = {}
menu_simulations.chase_player = {}
menu_simulations.big_defense = {}
menu_simulations.brutal_defeat = {}
menu_simulations.spider_ponds = {}

local _old_require = require

require = function(modname)
    if modname == "__base__/menu-simulations/menu-simulations" then
        return menu_simulations
    end
    modname = string.gsub(modname, "__base__", "./factorio-data-master/base")
    modname = string.gsub(modname, "__core__", "./factorio-data-master/core")
    --print(modname)
    return _old_require(modname)
end

defines = {
    direction = {
        north = 0,
        northeast = 1,
        east = 2,
        southeast = 3,
        south = 4,
        southwest = 5,
        west = 6,
        northwest = 7
    },
    difficulty_settings = {
        recipe_difficulty = {
            normal = 0,
            expensive = 1
        },
        technology_difficulty = {
            normal = 0,
            expensive = 1
        }
    }
}


local function add_path(path)
    package.path = path .. ";" .. package.path
end


local function add_signal(signals, name, type)
    signals[name] = {name = name, type =  type}
    signals["count"] = signals["count"] + 1
end


local function add_dict(signals, dict, type)
    local count = 0
    for k, v in pairs(data.raw[dict]) do
        if v.flags ~= nil then
            for j = 1, #v.flags do
                if v.flags[j] == "hidden" then
                    --print(v.name .. " is hidden")
                    goto continue
                end
            end
        end
        signals[k] = {name = k, type = type}
        signals["count"] = signals["count"] + 1
        count = count + 1
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


local function main()
    -- Apparently these are loaded from the start in some manner
    dofile("factorio-data-master/core/lualib/util.lua")
    dofile("factorio-data-master/core/lualib/dataloader.lua")

    --[[ Add the paths so that everything still works ]]
    add_path("./factorio-data-master/base/?.lua")
    add_path("./factorio-data-master/core/?.lua")
    add_path("./factorio-data-master/core/lualib/?.lua")

    --[[ Execute the data files in order ]]
    dofile("factorio-data-master/core/data.lua")
    dofile("factorio-data-master/base/data.lua")
    dofile("factorio-data-master/base/data-updates.lua")

    --[[ At this point data.raw should be initialized ]]

    --[[ Load Entities ]]

    -- what we need:
    -- name: obviously
    -- enable_inventory_bar: determines if entity should have BarMixin (true by default)
    -- circuit_wire_max_distance: determines if circuit connectable
    -- filter_count: determines if filter inserter or normal inserter

    -- Iterate over belts    

    -- Iterate over inserters
    --print(serpent.block(data.raw["inserter"]["burner-inserter"]["filter_count"]))
    for k, v in pairs(data.raw["inserter"]) do
        print(k, v["filter_count"], v["circuit_wire_max_distance"])
    end

    --[[ Load Tiles ]]

    -- We're gonna load all tiles regardless of anything
    -- This means that potentially valid blueprints will be constructed with
    -- tiles that cannot be placed within a blueprint
    -- In that case its left as an exercise of the blueprint maker to ensure
    -- they only use the correct tiles within them

    local tiles = {}

    for k, v in pairs(data.raw["tile"]) do
        --print(k)
        tiles[#tiles+1] = k
    end

    --scrape_tiles(tiles, "item")

    --print(serpent.block(tiles))

    local tiles_file = io.open("factoriotools/tile_data.py", "w")
    tiles_file:write("# tile_data.py\n")
    tiles_file:write("tile_names = {\n")
    for i = 1, #tiles do
        tiles_file:write("\t\"" .. tiles[i] .. "\",\n")
    end
    tiles_file:write("}")
    tiles_file:close()

    --[[ Load Signals ]]

    local signals = {}
    local item_signals = {}
    local fluid_signals = {}
    local virtual_signals = {}
    signals["count"] = 0
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

    for k, _ in pairs(signals) do
        item_signals[#item_signals+1] = k
    end

    -- Load Fluid SignalIDs
    add_dict(signals, "fluid", "fluid")
    for k, _ in pairs(data.raw["fluid"]) do
        fluid_signals[#fluid_signals+1] = k
    end
    -- Load Virtual SignalIDs
    add_dict(signals, "virtual-signal", "virtual")
    for k, _ in pairs(data.raw["virtual-signal"]) do
        virtual_signals[#virtual_signals+1] = k
    end

    --compare_difference(signals, should_have)

    -- Sort signals


    --[[ Create a Python-readable data file with the signal data contents: ]]
    local signals_file = io.open("factoriotools/signal_data.py", "w")
    signals_file:write("# signal_data.py\n")
    signals_file:write("# Autogenerated with 'update_data.lua'\n")
    signals_file:write("from .signalID import SignalID\n") -- this is way better
    signals_file:write("signal_IDs = {\n")
    for k, v in pairs(signals) do
        local output_string = ""
        if k ~= "count" then -- ignore count, dummy var
            output_string = "    \"" .. k .. "\": SignalID(\"" .. v.name
            output_string = output_string .. "\", \"" .. v.type .. "\"),\n"
            signals_file:write(output_string)
        end
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

    -- different way
    -- local signals_file = io.open("factorio/signals.py", "r+")
    -- local data = signals_file:read("a")

    -- --local s, e = string.find(data, "signalID = %b{}")
    -- --print(string.sub(data, s, e))

    -- data = string.gsub(data, "signalID = %b{}", "signalID = { 'wazzup': 'my nigga' }")
    -- print(data)

    -- signals_file:write(data)

    -- signals_file:close()
end

main()