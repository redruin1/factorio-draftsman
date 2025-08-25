-- interface.lua
---@diagnostic disable:lowercase-global
---@diagnostic disable:undefined-global

-- Rectifies issues loading the Factorio toolchain without the game itself.
-- All contents are subject to change.

-- Meta globals: these are used to keep track of ourselves during the load
-- process (since we have to do this manually due to reasons)
MOD_FOLDER_LOCATION = nil    -- Exactly where the mods are expected to be
MOD_LIST = nil      -- Total list of all mods; populated by Python
MOD_STACK = {}       -- Stack of mods keeping track of where to require files
MOD_DIR = nil       -- Path to the current mod (at the top of the mod tree)
CURRENT_FILE = nil  -- String filepath to the file we're currently executing
CURRENT_DIR = ""    -- Location of the filepath in some relative directory

-- Menu simulations: can be empty, but cannot be nil; not included in factorio-
-- data, so we supply dummy values
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

-- math.pow deprecated in Lua > 5.3; Factorio uses 5.2. Simple to fix:
-- (Deprecated since we now explicitly ask for Lua 5.2, but retained to help 
-- bridge compatibility if the user somehow cant get a copy of 5.2)
math.pow = math.pow or function(value, power)
    return value ^ power
end

-- Overwrite print to distinguish which "side" the message came from
local old_print = print
function print(...)
    old_print("LUA:", ...)
end

-- Display any logged messages if logging is enabled. Any error messages are
-- automatially displayed regardless of logging status.
-- Note that no log file is actually generated, and outputs are lost if not run
-- with parameter -l or --log
-- TODO: make this actually useful
function log(...)
    if LOG_ENABLED then
        print(...)
    end
end

-- Get size of lua dict. Factorio's version is implemented on the C++ side,
-- but this should be sufficient for our purposes
function table_size(t)
    local count = 0
    for _, _ in pairs(t) do
        count = count + 1
    end
    return count
end

-- Override the regular traceback with a prettier one that prints the actual
-- sections of the affected source code.
--old_traceback = debug.traceback
debug.traceback = function(message, level)

    print(message)

    local function get_function_name(info) 
        if info.name then
            return string.format("%s '%s'", info.namewhat, info.name)
        elseif info.what == "main" then
            return "main chunk"
        --elseif globals() then -- try a global name
            -- TODO
        elseif info.what ~= "C" then
            return string.format("function <%s:%d>", info.source, info.linedefined)
        else
            return "?"
        end
    end

    local stack_traces = ""
    level = level or 3
    local info = debug.getinfo(level, "nSlLf")
    while info do
        -- TODO: ignore our custom `require`

        local stack_trace = string.format(
            "\n\t%s:%d: in %s", info.source, info.currentline, get_function_name(info)
        )

        print(info.source)

        local source, err = py_get_source(info.source, info.currentline, package.path)

        if err == nil then
            stack_traces = stack_trace .. source .. stack_traces
        else
            stack_traces = stack_trace .. stack_traces
        end

        level = level + 1
        info = debug.getinfo(level, "nSlL")
    end
    return message .. "\nstack traceback:" .. stack_traces
end

-- Standardizes the lua require paths to standardized paths. Removes ".lua" from
-- the end, replaces all "." with "/", and changes "__modname__..." to
-- "mod/folder/location/modname/...". Does the same with "__base__" and 
-- "__core__", except they point to "factorio-data" instead. Also handles
-- a number of other miscellaneous cases in order to get the paths as normal as
-- possible.
-- Also returns a boolean `absolute`, which indicates if the filepath is 
-- considered absolute (from the root mods directory) or local (relative to
-- the top of `REQUIRE_STACK`)
local function normalize_module_name(module_name)
    -- remove lua from end if present
    module_name = module_name:gsub(".lua$", "")

    -- Normalize dots to paths, if appropriate
    -- First, check to see if there are any slashes in the path
    dot_path = module_name:find("[/\\]") == nil
    -- If not, we assume it's a dot separated path, so we convert to forward
    -- slashes for consistency
    if dot_path then
        module_name = module_name:gsub("%.", "/")
    end
    -- We do this because some slash paths can have dots in their folder names
    -- that should not be converted to path delimeters (Krastorio2)

    -- Some people like to specify their paths with a prepending dot to indicate
    -- the current folder like 'require(".config")' (FreightForwarding)
    -- In order to fix this, we check if the path starts with a slash, and then
    -- remove it if it does
    module_name = module_name:gsub("^/", "")

    -- Handle __mod-name__ format (alphanumeric + '-' + '_')
    local match, name = module_name:match("(__([%w%-_]+)__)")
    --print(modname, match, name)
    local absolute = true
    if name == "core" or name == "base" then
        module_name = string.gsub(module_name, match, "./factorio-data/"..name)
    elseif match ~= nil then
        -- Check if the name is the name of a currently enabled mod
        -- We need to do this because some people like to name their files
        -- "__init__.lua" or similar (FactorioExtended-Plus-Logistics)
        if mods[name] then
            --print(name.." is a recognized mod")
            -- Change '-' to '%-' so the following gsub doesn't treat them
            -- as special characters
            local correct_match = string.gsub(match, "%-", "%%-")
            --print(MOD_LIST[name].location)
            -- replace
            module_name = string.gsub(module_name, correct_match, MOD_LIST[name].location)
        else
            -- Can't determine what mod; use relative paths instead
            -- TODO: this should probably error with a better message
            assert(false, "Unknown mod " .. name)
        end
    else
        absolute = false
    end

    return module_name, absolute
end

-- Overwrite of require function. Normalizes the module name to make it easier
-- to interpret later, and manages a number of other things. After preprocessing
-- has taken place, `old_require` is called and executed at the end of the
-- function.
local old_require = require
function require(module_name)
    -- print("\tcurrent file:", REQUIRE_STACK[#REQUIRE_STACK])
    -- print("\trequiring:", module_name)

    local mod_changed = false
    local match, name = module_name:match("(__([%w%-_]+)__)")
    -- if the filepath uses this notation and the name is a mod, then we alter the current mod
    if match and mods[name] and MOD_STACK[#MOD_STACK] ~= MOD_LIST[name]then
        lua_push_mod(MOD_LIST[name])
        mod_changed = true
    end

    local norm_module_name, absolute = normalize_module_name(module_name)
    -- print("Normalized module name:", norm_module_name)

    local function get_parent(path)
        local pattern1 = "^(.+)/"
        local pattern2 = "^(.+)\\"

        if (string.match(path,pattern1) == nil) then
            return string.match(path,pattern2)
        else
            return string.match(path,pattern1)
        end
    end

    parent_dir = get_parent(norm_module_name)
    local path_added = false
    -- TODO: revise this logic to be better
    if absolute then
        local with_path = parent_dir .. "/?.lua"
        -- add the mod directory to the path if it's an absolute path
        if not absolute then with_path = MOD_DIR .. "/" .. with_path end

        lua_add_path(with_path)

        path_added = true
        table.insert(REQUIRE_STACK, norm_module_name) -- push
    else -- God this whole thing is scuffed
        -- get directory of current file
        local rel_parent = get_parent(REQUIRE_STACK[#REQUIRE_STACK]) or ""

        if not absolute then with_path = rel_parent .. "/?.lua" end -- MOD_DIR .. CURRENT_DIR
        lua_add_path(with_path)

        path_added = true
        table.insert(REQUIRE_STACK, rel_parent .. "/" .. norm_module_name) -- push
    end

    result = old_require(module_name)

    if path_added then
        --print("removed path")
        lua_remove_path()
        table.remove(REQUIRE_STACK) -- pop
    end

    if mod_changed then
        --print("removed mod")
        lua_pop_mod()
    end

    return result
end

-- Certain files are not included in the `factorio-data` repo for copyright 
-- reasons. As a result, attempting to load normally will encounter missing 
-- files, which Factorio itself does not handle. This function intercepts the 
-- beginning of the `require` process to see if it's (likely) one of these 
-- missing files, and then substitutes dummy values in their stead.

-- TODO: move this to the last step of the require process; that way you we'll
-- be able to handle both game cases elegantly, since files will be returned
-- properly if they exist, and only substituted with dummy values if they dont!
local missing_file_substitution = function(module_name)
    if module_name == "__base__/menu-simulations/menu-simulations" then
        return (function() return menu_simulations end)
    end

    local normal_name = normalize_module_name(module_name)

    local is_menu_simulations = string.match(normal_name, "menu%-simulations")
    local is_graphics = string.match(normal_name, ".*/?graphics/.+")
    local is_sounds = string.match(normal_name, ".*/?sound/.+")

    -- Infer the type of file that Factorio is expecting from the path, and then
    -- return a value corresponding to that type
    if is_menu_simulations then
        return (function() return {} end)
    elseif is_graphics then
        return (function() return { width=0, height=0, shift={0, 0}, line_length=0 } end)
    elseif is_sounds then
        return (function() return {type="sound", name=module_name} end)
    end
end

-- Wrapper function for `python_require` on the env.py side of things. Attempts
-- to read from the python zipfile archives first and continues with regular
-- lua file loading afterwards.
local archive_searcher = function(module_name)
    module_name, _ = normalize_module_name(module_name)

    local contents, err = python_require(MOD_STACK[#MOD_STACK], MOD_FOLDER_LOCATION, module_name, package.path)
    if contents then
        return assert(load(contents, MOD_STACK[#MOD_STACK].location .. "/" .. module_name))
    else
        return err
    end
end

-- Function that replaces the regular Lua file searching. Identical in function
-- except that it doesn't convert dots to slashes; we manually take care of that
-- ourselves in `normalize_module_name`. Every path passed into this function
-- expects to be in a literal path format, hence the name.
local literal_searcher = function(module_name)
    local norm_module_name, _ = normalize_module_name(module_name)
    --print(package.path)

    local errmsg = ""
    for path in string.gmatch(package.path, "([^;]+)") do
        local filename = string.gsub(path, "%?", norm_module_name)
        --local file, err = io.open(filename, "rb")
        --local file_string, err = python_file_to_string(filename)
        local file, err = python_get_file(filename)
        if file then
            --print(file, err)
            --print("loaded from file: " .. filename)
            -- Compile and return the module
            --result = assert(load(assert(file:read("*a")), module_name))
            --result = assert(load(file_string, module_name))
            result = assert(load(file.read(), module_name))
            file.close() -- make sure we close that bitch
            --CURRENT_DIR = filename
            return result
        else
            --print(err)
        end
        errmsg = errmsg.."\n\tno file '"..filename.."' (checked with custom loader)"
    end
    return errmsg
end

-- search order:
-- 1. missing_file_substitution (returns dummy data so that Factorio doesn't explode)
-- 2. archive_searcher (defers to python and searches one of the zip files)
-- 3. package.preload (returns a copy if already loaded once in this session)
-- 4. literal_searcher (overwrites file searcher, identical but with some custom behavior)
-- 5. C lib searcher (unused)
-- 6. All-in-one searcher (unused)
table.insert(package.searchers, 1, missing_file_substitution)
table.insert(package.searchers, 2, archive_searcher)
package.searchers[4] = literal_searcher

-- =================
-- Interface Helpers
-- =================

-- Alter the package.path to include new directories to search through.
function lua_add_path(path)
    package.path = path .. ";" .. package.path
end

-- Remove the first path from package.path. Make sure not to remove system ones!
function lua_remove_path()
    pos = package.path:find(";") + 1
    package.path = package.path:sub(pos)
end

-- (Re)set the package path to some known value
function lua_set_path(path)
    package.path = path
end

-- Unloads all files. Lua has a package.preload functionality where files are
-- only included once and reused as necessary. This can cause problems when two
-- files have the exact same name however; If mod A has a file named "utils" and
-- is loaded first, mod B will require "utils" and will get A's copy of the file
-- instead of loading mod B's copy.
-- To prevent this, we unload all required files every time we load a stage,
-- which is excessive but (hopefully) guarantees correct behavior.
function lua_unload_cache()
    for k, _ in pairs(package.loaded) do
        package.loaded[k] = nil
    end
end

-- Push a mod to the stack of mods that the current require chain is using
function lua_push_mod(mod)
    table.insert(MOD_STACK, mod)
    MOD_DIR = MOD_STACK[#MOD_STACK].location
end

-- Pop a mod off the stack of mods that the current require chain is using
function lua_pop_mod()
    table.remove(MOD_STACK)
    MOD_DIR = MOD_STACK[#MOD_STACK].location
end

-- Wipe all mods from the mod tree to return it to a known state 
-- (on stage change)
function lua_wipe_mods()
    MOD_STACK = {}
    MOD_DIR = nil
    REQUIRE_STACK = {}
end