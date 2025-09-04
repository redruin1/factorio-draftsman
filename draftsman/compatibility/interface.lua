-- interface.lua
---@diagnostic disable:lowercase-global
---@diagnostic disable:undefined-global

-- Rectifies issues loading the Factorio toolchain without the game itself.
-- All contents are subject to change.

-- Meta globals: these are used to keep track of ourselves during the load
-- process (since we have to do this manually due to reasons)
REQUIRE_STACK = {}  -- Stack of files representing the current `require()` tree
MOD_STACK = {}      -- Stack of mods keeping track of where to `require()` files

-- ================
-- Versioning Fixes
-- ================

-- math.pow deprecated in Lua > 5.3; Factorio uses 5.2. Simple to fix:
-- (Shouldn't need this since we now explicitly ask for Lua 5.2, but retained to 
-- help bridge compatibility if the user somehow cant get a copy of 5.2)
math.pow = math.pow or function(value, power)
    return value ^ power
end

-- Factorio uses Lua 5.2.1 - Lupa uses 5.2.4. Inbetween these two versions the
-- semantics of table.insert/remove changed slightly - for now we just overwrite
-- the new implementation with one that mimics the old behavior
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

-- ===================
-- Interface Functions
-- ===================

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
    local info = debug.getinfo(level, "nSlL")
    while info do
        -- Ignore both our custom `require` and lua C require (since  they're 
        -- not relevant)
        if info.name ~= "require" and info.name ~= "lua_require" then
            local stack_trace = string.format(
                "\n\t%s:%d: in %s\n", info.source, info.currentline, get_function_name(info)
            )
            local source, err = py_get_source_lines(info.source, info.currentline)

            -- Insert the stack trace in reverse order so latest is last
            if err == nil then
                stack_traces = stack_trace .. source .. stack_traces
            else
                stack_traces = stack_trace .. stack_traces
            end
        end

        level = level + 1
        info = debug.getinfo(level, "nSlL")
    end
    -- print(message .. "\nstack traceback:" .. stack_traces)
    -- debug.debug()
    return message .. "\nstack traceback:" .. stack_traces
end

-- Standardizes the lua require paths to regular-like paths. Removes ".lua" from
-- the end, converts dot paths to slash paths, converts all backslashes to 
-- forward slashes, etc.
-- Also returns a boolean `absolute`, which indicates if the filepath is 
-- considered absolute (from the root mods directory) or local (relative to
-- the top of `REQUIRE_STACK`)
local function normalize_module_name(module_name)
    -- Remove lua from end (if present) in order to make it compatible with
    -- `package.path` syntax
    module_name = module_name:gsub(".lua$", "")

    -- If the module starts with `./` or `.`, then this is a special (redundant) 
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

    if module_name[1] == "/" then
        -- If the path still starts with a `/` at this point, then it must refer 
        -- to an absolute path. In Factorio terms, this means it originates from 
        -- the root folder of the importing mod
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
            end
        end
    end
    -- Otherwise, it's a relative path and the actual resolved path is 
    -- determined via searching `package.path`
    return module_name, false
end

-- Removes the child-most file/folder from a path.
local function get_parent(path)
    -- We only have to check forward slashes because all paths are normalized
    -- when this function is used
    if path then
        return string.match(path, "^(.+)/")
    else
        return nil
    end
end

-- Overwrite of require function. Maintains a `REQUIRE_STACK` and a `MOD_STACK` 
-- to determine the paths of local files so they can be required properly. 
-- Manages `package.loaded` cache so that files are loaded at the correct time.
local lua_require = require
function require(module_name)
    --print("\tcurrent file:", REQUIRE_STACK[#REQUIRE_STACK])
    --print("\trequiring:", module_name)

    -- Normalize the module name and determine whether it's an absolute path or
    -- not
    local norm_module_name, absolute = normalize_module_name(module_name)
    --print("Normalized module name:", norm_module_name)

    -- Check to see if the mod specifies a path with the `__mod-name__` format,
    -- and if `mod-name` is not the currently active mod, change contexts to the
    -- newly specified one
    local mod_changed = false
    local match, name = module_name:match("(__([%w%-_]+)__)")
    if match and MOD_LIST[name] and MOD_STACK[#MOD_STACK] ~= MOD_LIST[name] then
        lua_push_mod(MOD_LIST[name])
        mod_changed = true
    end

    -- Determine the "new" `current_file` once we begin to require the file
    local path_added = false
    local current_file
    if absolute then
        -- Path is already absolute; set it as the new "current file"
        current_file = norm_module_name .. ".lua"
    else
        -- Relative path; get the parent of the old current file
        local parent = get_parent(REQUIRE_STACK[#REQUIRE_STACK])

        if parent then
            -- In order to look for files in the same location as the current file, 
            -- we add the parent folder to `package.path`
            lua_add_path(parent .. "/?.lua")
            path_added = true

            -- New current file is the constructed absolute path from parent and 
            -- module name
            current_file = parent .. "/" .. norm_module_name .. ".lua"
        else
            current_file = norm_module_name .. ".lua"
        end
    end

    -- Push the new `current_file` to the stack so that any recursive requires
    -- have the correct new filename
    table.insert(REQUIRE_STACK, current_file)

    -- Call the original C Lua require function.
    -- We MUST use the original `module_name` here, otherwise mod behaviors that
    -- specifically look for this string will fail in creative ways 
    -- (pyanodons, flib, Kuxynators)
    result = lua_require(module_name)

    -- After the file is required, we reset it's cache so subsequent requires
    -- of the same filename will run through the require process again.
    -- This won't reload children files in parents that require them simply, but
    -- it ensures that when two different files share the same exact filename
    -- both will be loaded properly
    package.loaded[module_name] = nil

    -- After the require function finishes, the current file can be popped off
    table.remove(REQUIRE_STACK)

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

-- Treat the current mod as an archive and look for files inside of it, 
-- returning the file contents if found.
local archive_searcher = function(module_name)
    local norm_module_name, absolute = normalize_module_name(module_name)

    local contents, err = py_search_archive(MOD_STACK[#MOD_STACK], norm_module_name, package.path)
    if contents then
        local source_name
        if not absolute then
            source_name = (get_parent(REQUIRE_STACK[#REQUIRE_STACK - 1]) or "") .. "/" .. norm_module_name
        else
            source_name = norm_module_name
        end
        return assert(load(contents, source_name .. ".lua"))
    else
        return err
    end
end

-- Function that replaces the regular Lua file searching. Identical in function
-- except that it normalizes the path and resolves the `__mod-name__` syntax to
-- the corresponding mod location.
local folder_searcher = function(module_name)
    local norm_module_name, absolute = normalize_module_name(module_name)

    local errmsg = ""
    for path in string.gmatch(package.path, "([^;]+)") do
        local filename = string.gsub(path, "%?", norm_module_name)

        -- Convert __mod-name__ format into the actual mod filepath
        -- TODO: should this format even exist in package.path?
        local match, name = filename:match("(__([%w%-_]+)__)")
        if match ~= nil and MOD_LIST[name] then
            -- Change '-' to '%-' so the following gsub doesn't treat them
            -- as special characters
            local correct_match = string.gsub(match, "%-", "%%-")
            -- replace
            filename = string.gsub(filename, correct_match, MOD_LIST[name].location)
        end

        -- Try to load the file on the Python side (so we can take advantage of
        -- it's better byte encoding handling)
        local file = py_get_file(filename)
        if file then
            -- print("Found folder file ", filename);
            -- Try to resolve as much of the path as possible
            local source_name
            if not absolute then
                source_name = (get_parent(REQUIRE_STACK[#REQUIRE_STACK - 1]) or "") .. "/" .. norm_module_name
            else
                source_name = norm_module_name
            end

            -- Compile and return the module
            result = assert(load(file.read(), source_name .. ".lua"))

            file.close() -- make sure we close the file handle
            return result
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

package.searchers = {
    archive_searcher,
    folder_searcher,
    missing_file_substitution
}

-- =================
-- Interface Helpers
-- =================

-- Alter the package.path to include new directories to search through (before
-- others).
function lua_add_path(path)
    package.path = path .. ";" .. package.path
end

-- Remove the first path from package.path. Probably a bad idea to remove system
-- ones!
function lua_remove_path()
    pos = package.path:find(";") + 1
    package.path = package.path:sub(pos)
end

-- (Re)set the package path to some known value.
function lua_set_path(path)
    package.path = path
end

-- Unloads all files. Lua has a `package.loaded` functionality where files are
-- only included once and reused as necessary. This can cause problems when two
-- files have the exact same name however; If mod A has a file named "utils" and
-- is loaded first, mod B will require "utils" and will get A's copy of the file
-- instead of loading mod B's copy.
-- To prevent this, we unload all required files every time we load each 
-- individual mod stage, which should (help) ensure correct loading behavior.
function lua_unload_cache()
    for k in pairs(package.loaded) do
        package.loaded[k] = nil
    end
end

-- Push a mod to the stack of mods that the current require chain is using
function lua_push_mod(mod)
    table.insert(MOD_STACK, mod)
end

-- Pop a mod off the stack of mods that the current require chain is using
function lua_pop_mod()
    table.remove(MOD_STACK)
end

-- Wipe all mods and requires from the mod tree to return it to a known state 
-- (on stage change)
function lua_stage_reset()
    MOD_STACK = {}
    REQUIRE_STACK = {}
end