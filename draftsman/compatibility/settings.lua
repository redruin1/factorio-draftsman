-- settings.lua

-- Bridges the gap from the settings lifecycle to the data lifecycle.
-- Converts the settings data stored in data.raw and stores it in the global
-- table 'settings'.

---@diagnostic disable:lowercase-global

-- Factorio and Factorio mods use this for serialization/debugging, so we
-- include it as well
serpent = require("compatibility.serpent")

settings = {}
settings["startup"] = {}
settings["runtime-global"] = {}
settings["runtime-per-user"] = {}
settings.startup = settings["startup"]
settings.global = settings["runtime-global"]
settings.player = settings["runtime-per-user"]

-- Iterate over each setting type and place it in it's proper location
local function set_settings(type)
    local setting_list = data.raw[type] or {} -- pragma: undefined-global
    for name, setting in pairs(setting_list) do
        setting.value = setting.default_value
        settings[setting.setting_type][name] = setting
    end
end

set_settings("bool-setting")
set_settings("int-setting")
set_settings("double-setting")
set_settings("string-setting")