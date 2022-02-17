-- compatability.lua

-- Rectifies issues loading the Factorio toolchain without the game itself.
-- All contents are subject to change.

-- Meta globals:
MOD = {}
MOD_NAME = ""
MOD_DIR = ""

-- Not technically necessary, but lets keep it anyway, seems useful
serpent = require("factoriotools.compatability.serpent")

-- Menu simulations: can't be empty, but cannot be nil
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

-- Some defines that are absolutely needed
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

-- math.pow deprecated in Lua > 5.3; Factorio uses 5.1. Simple to fix
math.pow = math.pow or function(value, power)
    return value ^ power
end

-- TODO: see if log exists within data or if its virtual
-- maybe create a custom log? probably excessive, this aint a debugger
function log(message) end

-- Get size of lua dict. Factorio's version is implemented on the C++ side,
-- but this should do
function table_size(t)
    local count = 0
    for k,v in pairs(t) do
        count = count + 1
    end
    return count
end

-- Fix for Factorio using "__base__" and "__core__" instead of actual paths:
-- local _old_require = require
-- require = function(modname)
--     if modname == "__base__/menu-simulations/menu-simulations" then
--         return menu_simulations
--     end

--     -- the plot thickens

--     local match, name = modname:match("(__(%D+)__)")

--     --print(match, name)
--     if match == "__core__" then
--         modname = string.gsub(modname, "__core__", "./factorio-data-master/core")
--     elseif match == "__base__" then
--         modname = string.gsub(modname, "__base__", "./factorio-data-master/base")
--     elseif match ~= nil then
--         --print(modname, match)
        
--         local correct_match = string.gsub(match, "%-", "%%-")
--         --print(correct_match)
--         modname = string.gsub(modname, correct_match, "./factorio-mods/" .. name)
--     end

--     --print("\t", modname)

--     modname = string.gsub(modname, ".lua$", "")

--     -- Attempt to require the file
--     -- local success, result = pcall(_old_require, modname)
--     -- if success then
--     --     return result
--     -- else -- if failed, the file is most likely still zipped inside the archive
--     --     print("bruh moment")
--     --     error(result)
--     -- end
--     return _old_require(modname)
-- end

-- keep track of all mods required in a particular session
required_in_session = {}
paths_in_session = {}

local function normalize_module_name(modname)
    -- remove lua from end if present
    modname = modname:gsub(".lua$", "")

    -- normalize dots to paths
    modname = modname:gsub("%.", "/")

    -- Handle __mod-name__ format
    local match, name = modname:match("(__(%D+)__)")
    --print(modname, match)
    -- if match == "__core__" then
    --     modname = string.gsub(modname, "__core__", "./factorio-data-master/core")
    -- elseif match == "__base__" then
    --     modname = string.gsub(modname, "__base__", "./factorio-data-master/base")
    local absolute = true
    if name == "core" or name == "base" then
        modname = string.gsub(modname, match, "./factorio-data-master/" .. name)
    elseif match ~= nil then
        local correct_match = string.gsub(match, "%-", "%%-")
        modname = string.gsub(modname, correct_match, "./factorio-mods/" .. name)
    else
        absolute = false
    end

    return modname, absolute
end

local old_require = require
function require(module_name)
    --print("\trequiring:", module_name)
    local absolute
    module_name, absolute = normalize_module_name(module_name)
    --print("Normalized module name:", module_name)    
    required_in_session[module_name] = true
    CURRENT_FILE = module_name

    -- if not, try again after adding the path to the currently executing file
    --print("CURRENT_FILE:", CURRENT_FILE)

    local function get_parent(path)
        local pattern1 = "^(.+)/"
        local pattern2 = "^(.+)\\"

        if (string.match(path,pattern1) == nil) then
            return string.match(path,pattern2)
        else
            return string.match(path,pattern1)
        end
    end

    PARENT_DIR = get_parent(module_name)
    --print("PARENT_DIR:", PARENT_DIR)
    --print(paths_in_session[PARENT_DIR])
    if PARENT_DIR and not paths_in_session[PARENT_DIR] then
        local with_path = PARENT_DIR .. "/?.lua"
        -- add the base directory to the thing
        if not absolute then with_path = MOD_DIR .. "/" .. with_path end
        ADD_PATH(with_path)
        --print("added path:", with_path)
        paths_in_session[PARENT_DIR] = true
    end

    return old_require(module_name)
end


local menu_simulations_searcher = function(modname)
    -- this doesn't exist, pretend like it does
    if modname == "./factorio-data-master/base/menu-simulations/menu-simulations" then
        return (function() return menu_simulations end)
    end
end


local archive_searcher = function(modname)
    --print("custom_searcher!")

    -- for k, _ in pairs(package.loaded) do
    --     print(k)
    -- end

    --print("Attempting to find " .. modname .. " in python:")

    local contents, err = python_require(MOD, modname, package.path)
    if contents then
        return assert(load(contents, modname))
    else
        return err
    end
end

table.insert(package.searchers, 1, menu_simulations_searcher)
-- zip archives are prioritized more than file folders
table.insert(package.searchers, 2, archive_searcher)

-- we've loaded the mod names and their versions into `python_mods`
-- `python_mods` is still a python object though; here we copy it to a lua table
-- TODO? maybe keep python_mods around and use it for things
mods = {}
for k in python.iter(python_mods) do
    mods[k] = python_mods[k]
end

-- =========
-- Interface
-- =========

-- Alter the package.path to include the directories to search through:
function ADD_PATH(path)
    package.path = path .. ";" .. package.path
end

-- (Re)set the package path
function SET_PATH(path)
    package.path = path
end

function UNLOAD_SESSION_CACHE()
    for k, _ in pairs(required_in_session) do
        package.loaded[k] = nil
    end
end

function UNLOAD_ENTIRE_CACHE()
    for k, _ in pairs(package.loaded) do
        package.loaded[k] = nil
    end
end

function RESET_MOD_STATE()
    required_in_session = {}
    paths_in_session = {}
end