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
local lua_print = print
function print(...)
    lua_print("LUA:", ...)
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

-- Factorio uses Lua 5.2.1 - Lupa uses 5.2.4. Inbetween these two versions the
-- semantics of table.insert/remove changed slightly - for now we just overwrite
-- the new implementations with ones that mimic the old behavior
table_remove_5_2_4 = table.remove
function table_remove_5_2_1(t, idx)
    idx = idx ~= nil and idx or #t
    if t[idx] then
        return table_remove_5_2_4(t, idx)
    else
        return nil
    end
end
table.remove = table_remove_5_2_1

-- Override the regular traceback with a prettier one that prints the actual
-- sections of the affected Lua source code.
debug.traceback = function(message, level)
    -- Message can be nil - make it an empty string in that case
    message = (message == nil) and "" or message

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
    level = level or 2
    local info = debug.getinfo(level, "nSlLf")
    while info do
        -- Ignore both our custom `require` and lua C require (since  they're 
        -- not relevant)
        if info.name ~= "require" and info.name ~= "lua_require" then

            local stack_trace = string.format(
                "\n\t%s:%d: in %s\n", info.source, info.currentline, get_function_name(info)
            )

            -- print(info.source)

            local source, err = py_get_source(info.source, info.currentline, package.path)

            if err == nil then
                stack_traces = stack_trace .. source .. stack_traces
            else
                stack_traces = stack_trace .. stack_traces
            end

        end

        level = level + 1
        info = debug.getinfo(level, "nSlL")
    end
    --print(message .. "\nstack traceback:" .. stack_traces)
    --debug.debug()
    return message .. "\nstack traceback:" .. stack_traces
end

-- Removes the child-most file/folder from a path, leaving just the parent 
-- folders.
local function get_parent(path)
    local pattern1 = "^(.+)/"
    local pattern2 = "^(.+)\\"

    if (string.match(path,pattern1) == nil) then
        return string.match(path,pattern2)
    else
        return string.match(path,pattern1)
    end
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

-- This function has to 
-- * remove `.lua`
-- * convert dots to slashes
-- * prepend the current parent folder if not an absolute path
-- so `data-duplicate-checker.lua` turns into `__core__/lualib/data-duplicate-checker`
-- This must be done like this so that 
-- 1. Internal paths remain how mods expect them
-- 2. `require` has no ambiguity between different modules with the same name in different packages
-- The actual resolution of __mod-name__ to a true path is beyond the scope of this function
local function normalize_module_name(module_name)
    -- Remove lua from end if present
    module_name = module_name:gsub(".lua$", "")

    -- If the module starts with `./` or `.`, then this is special (redundant) 
    -- relative import syntax and can be safely removed
    if module_name[1] == "." then
        if module_name[2] == "/" then
            module_name = module_name:gsub("%./", "")
        else
            module_name = module_name:gsub("%.", "")
        end
    end

    -- Normalize dots to paths, if appropriate
    -- Certain slash paths can have dots in their folder names (Krastorio2), so
    -- we check to make sure it's a "pure" dot path with no slashes before 
    -- converting
    dot_path = module_name:find("[/\\]") == nil
    if dot_path then
        -- Convert dots to forward slashes
        module_name = module_name:gsub("%.", "/")
    end

    -- Normalize any back slashes to forward slashes (plays better with archives)
    module_name = module_name:gsub("\\", "/")

    -- Some people like to specify their paths with a prepending dot to indicate
    -- the current folder like 'require(".config")' (FreightForwarding)
    -- In order to fix this, we check if the path starts with a slash, and then
    -- remove it if it does
    -- module_name = module_name:gsub("^/", "")

    local absolute = false
    if module_name[1] == "/" then
        -- If the path still starts with a `/` at this point, then it must refer 
        -- to an absolute path. In Factorio terms, this means it originates from 
        -- the root folder of the importing mod
        absolute = true
        module_name = MOD_STACK[#MOD_STACK].name .. module_name
        return module_name, true
    else
        -- Similarly if the path specifies `__mod-name__`, then that path is
        -- also absolute (just relative to a different mod root)
        local match, name = module_name:match("(__([%w%-_]+)__)")
        if match then
            -- Check if the name is the name of a currently enabled mod
            -- We need to do this because some people like to name their files
            -- "__init__.lua" or similar (FactorioExtended-Plus-Logistics)
            if MOD_LIST[name] then
                absolute = true
                return module_name, true
            else
                -- error("Unknown mod " .. mod)
            end
        end
    end

    -- Otherwise, we need to prepend the current mod name in __mod-name__
    -- format
    -- module_name = get_parent(REQUIRE_STACK[#REQUIRE_STACK]) .. "/" .. module_name

    return module_name, false
end

-- Overwrite of require function. Normalizes the module name to make it easier
-- to interpret later, and manages a number of other things. After preprocessing
-- has taken place, `old_require` is called and executed at the end of the
-- function.
local lua_require = require
function require(module_name)
    -- print("\tcurrent file:", REQUIRE_STACK[#REQUIRE_STACK])
    -- print("\trequiring:", module_name)

    -- Normalize the module name and determine whether it's an absolute path or
    -- not
    local norm_module_name, absolute = normalize_module_name(module_name)

    -- Check to see if the mod specifies a path with the `__mod-name__` format,
    -- and if `mod-name` is not the currently active mod, change contexts to the
    -- newly specified one
    local mod_changed = false
    local match, name = module_name:match("(__([%w%-_]+)__)")
    if match and MOD_LIST[name] and MOD_STACK[#MOD_STACK] ~= MOD_LIST[name] then
        lua_push_mod(MOD_LIST[name])
        mod_changed = true
    end

    local path_added = false
    if absolute then
        -- Path is already absolute; set it as the new "current file"
        table.insert(REQUIRE_STACK, norm_module_name)
    else
        -- Relative path; get the parent of the current file
        local parent = get_parent(REQUIRE_STACK[#REQUIRE_STACK])

        -- In order to look for files in the same location as the current file, 
        -- we add the parent folder to `package.path`
        lua_add_path(parent .. "/?.lua")
        path_added = true

        -- Current file is the constructed absolute path from parent and module
        -- name
        table.insert(REQUIRE_STACK, parent .. "/" .. norm_module_name)
    end

    -- TODO: FIXME
    -- Temporary, until I figure out how Factorio handles `package.loaded`
    --lua_unload_cache()

    -- local package_loaded_copy = shallowcopy(package.loaded)

    -- Call the original Lua require function.
    -- We MUST use the original `module_name` here, otherwise mod behaviors that
    -- specifically look for this string will fail in creative ways 
    -- (flib, Kuxynators)
    result = lua_require(module_name)

    --package.loaded = package_loaded_copy
    -- local markDeletion = {}
    -- local markModify = {}
    -- for name in pairs(package.loaded) do
    --     if not package_loaded_copy[name] then
    --         table.insert(markDeletion, name)
    --     elseif package_loaded_copy[name] ~= package.loaded[name] then
    --         table.insert(markModify, name)
    --     end
    -- end
    -- for _, name in pairs(markDeletion) do
    --     package.loaded[name] = nil
    -- end
    -- for _, name in pairs(markModify) do
    --     package.loaded[name] = package_loaded_copy[name]
    -- end
    -- for name in pairs(package.loaded) do
    --     package.loaded[name] = package_loaded_copy[name]
    -- end

    package.loaded[module_name] = nil

    -- After the require function finishes, the current file has now completed 
    -- and can return control back to the caller
    table.remove(REQUIRE_STACK) -- pop

    -- If we added a local path to `package.path`, tidy up
    if path_added then
        lua_remove_path()
    end

    -- If we changed mod contexts to load a file, tidy up
    if mod_changed then
        lua_pop_mod()
    end

    return result
end

-- Wrapper function for `python_require` on the env.py side of things. Attempts
-- to read from the python zipfile archives first and continues with regular
-- lua file loading afterwards.
local archive_searcher = function(module_name)
    --print("Archive search")
    local norm_module_name, absolute = normalize_module_name(module_name)

    local contents, err = python_require(MOD_STACK[#MOD_STACK], MOD_FOLDER_LOCATION, norm_module_name, package.path)
    if contents then
        local source_name = norm_module_name
        if not absolute then
            source_name = (get_parent(REQUIRE_STACK[#REQUIRE_STACK]) or "") .. "/" .. norm_module_name
        end
        return assert(load(contents, source_name .. ".lua"))
    else
        return err
    end
end

-- Function that replaces the regular Lua file searching. Identical in function
-- except that it doesn't convert dots to slashes; we manually take care of that
-- ourselves in `normalize_module_name`. Every path passed into this function
-- expects to be in a literal path format, hence the name.
local literal_searcher = function(module_name)
    -- This function needs a true path to a file
    --print("Literal search")
    module_name, _ = normalize_module_name(module_name)
    -- print(norm_module_name)
    -- print(package.path)
    --print(module_name)

    local errmsg = ""
    for path in string.gmatch(package.path, "([^;]+)") do
        local filename = string.gsub(path, "%?", module_name)

        -- Convert __mod-name__ format into the actual mod filepath
        local match, name = filename:match("(__([%w%-_]+)__)")
        if match ~= nil and MOD_LIST[name] then
            --print(name.." is a recognized mod")
            -- Change '-' to '%-' so the following gsub doesn't treat them
            -- as special characters
            local correct_match = string.gsub(match, "%-", "%%-")
            --print(MOD_LIST[name].location)
            -- replace
            filename = string.gsub(filename, correct_match, MOD_LIST[name].location)
        end

        --local file, err = io.open(filename, "rb")
        --local file_string, err = python_file_to_string(filename)
        local file, err = python_get_file(filename)
        if file then
            --print(file, err)
            --print("loaded from file: " .. filename)
            -- Compile and return the module
            --result = assert(load(assert(file:read("*a")), module_name))
            --result = assert(load(file_string, module_name))
            result = assert(load(file.read(), module_name .. ".lua"))
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

-- Certain files are not included in the `factorio-data` repo for copyright 
-- reasons. As a result, attempting to load normally will encounter missing 
-- files, which Factorio itself does not handle. This function intercepts the 
-- beginning of the `require` process to see if it's (likely) one of these 
-- missing files, and then substitutes dummy values in their stead.
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
        return (function() return { type="sound", name=module_name } end)
    end
end

-- search order:
-- 1. archive_searcher (defers to python and searches one of the zip files)
-- 2. package.preload (returns a copy if already loaded once in this session)
-- 3. literal_searcher (overwrites file searcher, identical but with some custom behavior)
-- 4. C lib searcher (unused)
-- 5. All-in-one searcher (unused)
-- 6. missing_file_substitution (returns dummy data so that Factorio doesn't explode)
table.insert(package.searchers, 1, archive_searcher)
package.searchers[3] = literal_searcher
table.insert(package.searchers, missing_file_substitution)

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

-- Unloads all files. Lua has a package.loaded functionality where files are
-- only included once and reused as necessary. This can cause problems when two
-- files have the exact same name however; If mod A has a file named "utils" and
-- is loaded first, mod B will require "utils" and will get A's copy of the file
-- instead of loading mod B's copy.
-- To prevent this, we unload all required files every time we load a stage,
-- which is excessive but (hopefully) guarantees correct behavior.
-- TODO: this could probably be removed if we used absolute paths for all
-- requires, so `__base__/utils` would be distinguishable from `__mod__/utils`
function lua_unload_cache()
    -- for k, _ in pairs(package.loaded) do
    --     package.loaded[k] = nil
    -- end
end

-- Push a mod to the stack of mods that the current require chain is using
function lua_push_mod(mod)
    table.insert(MOD_STACK, mod)
end

-- Pop a mod off the stack of mods that the current require chain is using
function lua_pop_mod()
    table.remove(MOD_STACK)
end

-- Wipe all mods from the mod tree to return it to a known state 
-- (on stage change)
function lua_wipe_mods()
    MOD_STACK = {}
    REQUIRE_STACK = {}
end