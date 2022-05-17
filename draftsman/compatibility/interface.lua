-- interface.lua

-- Rectifies issues loading the Factorio toolchain without the game itself.
-- All contents are subject to change.

---@diagnostic disable:lowercase-global

-- Meta globals:
MOD_LIST = nil
MOD = nil
MOD_NAME = nil
MOD_DIR = nil

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

-- math.pow deprecated in Lua > 5.3; Factorio uses 5.1. Simple to fix:
math.pow = math.pow or function(value, power)
    return value ^ power
end

-- maybe create a custom log? Probably excessive, I need a debugger for MY code,
-- not the mod's
function log(message) end

-- Add a prepended message to distinguish which "side" the message came from
local old_print = print
function print(...)
    old_print("LUA:", ...)
end

-- Get size of lua dict. Factorio's version is implemented on the C++ side,
-- but this should be sufficient for our purposes
function table_size(t)
    local count = 0
    for k,v in pairs(t) do
        count = count + 1
    end
    return count
end

-- keep track of all mods required in a particular session (do we need this?)
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

    local absolute = true
    if name == "core" or name == "base" then
        modname = string.gsub(modname, match, "./factorio-data/"..name)
    elseif match ~= nil then
        local correct_match = string.gsub(match, "%-", "%%-")
        modname = string.gsub(modname, correct_match, "./factorio-mods/"..name)
    else
        absolute = false
    end

    return modname, absolute
end

-- TODO: fix this
local old_require = require
function require(module_name)
    --print("\trequiring:", module_name)
    local absolute
    module_name, absolute = normalize_module_name(module_name)
    --print("Normalized module name:", module_name, absolute)
    required_in_session[module_name] = true
    CURRENT_FILE = module_name

    --print(package.path)

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
    -- local added = false
    if PARENT_DIR and not paths_in_session[PARENT_DIR] then
        local with_path = PARENT_DIR .. "/?.lua"
        -- add the mod directory to the path if it's an absolute path
        if not absolute then with_path = MOD_DIR .. "/" .. with_path end
        --print("\tWITH_PATH: " .. with_path)
        ADD_PATH(with_path)
        --print("added path:", with_path)
        paths_in_session[PARENT_DIR] = true
        -- added = true
    end

    result = old_require(module_name)

    -- if added then
    --     REMOVE_PATH()
    -- end

    return result
end


local menu_simulations_searcher = function(modname)
    -- this doesn't exist, pretend like it does
    if modname == "./factorio-data/base/menu-simulations/menu-simulations" then
        return (function() return menu_simulations end)
    end
end


function script_path()
    local str = debug.getinfo(2, "S").source:sub(2)
   return str:match("(.*[/\\])")
end

local archive_searcher = function(modname)
    --print("custom_searcher!")

    -- for k, _ in pairs(package.loaded) do
    --     print(k)
    -- end

    --print("Attempting to find " .. modname .. " in python:")

    local contents, err = python_require(MOD_LIST, MOD, modname, package.path)
    if contents then
        filepath = err .. "/?.lua"
        -- TODO: fix this
        --ADD_PATH(filepath)
        return assert(load(contents, modname))
    else
        return err
    end
end

table.insert(package.searchers, 1, menu_simulations_searcher)
-- zip archives are prioritized more than file folders
table.insert(package.searchers, 2, archive_searcher)

-- we've loaded the mod names and their versions into `python_mods`
-- `python_mods` is still a python object though; here we convert it to a lua table
---@diagnostic disable-next-line:lowercase-global
mods = {}
for k in python.iter(python_mods) do
    mods[k] = python_mods[k]
end

-- =========
-- Interface
-- =========

-- Alter the package.path to include the directories to search through.
-- We add them to the end to prioritize paths that were added first, such as the
-- core modules
-- NOTE: this might still cause problems in the future; we need some way to only
-- add the root part of the folder we're requesting, otherwise have the chance
-- of requesting a file located in the mod when we should be requesting the core
-- script...
-- I'm kicking this down the road for later though, it works for now
function ADD_PATH(path)
    package.path = package.path .. ";" .. path
end

-- Remove the first path from package.path. Make sure not to remove system ones!
-- function REMOVE_PATH()
--     pos = package.path:find(";") + 1
--     package.path = package.path:sub(pos)
-- end

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