# __init__.py
"""
Allows the user to import, create, manipulate, and export Factorio blueprint 
strings.

`draftsman` attempts to provide a convinient, 'one-stop-shop' solution to the
problem of programmatically creating blueprint strings, used for automation of 
designing structures that would be too tedius to build otherwise.

In addition to providing the bare functionality of importing and exporting, 
`draftsman` is designed with the developer in mind, and has a wide array of 
methods and classes designed to write clean, self-documenting scripts. 
`draftsman` is also well-documented, well-tested, and easy to install.

`draftsman` mimics the Factorio `data-life-cycle`[link] by extracting its data
directly from Wube's `factorio-data repository`[link]. This ensures continuity
between draftsman and Factorio, and also makes keeping draftsman up to date much
simpler. In addition, by loading the data in the same way as Factorio does, it
allows draftsman to not only work with the base game, but Factorio mods as well.
The user can simply drop their modlist into draftsman's mod-folder and update
the module to automatically manipulate modded entities, items, etc. If you would
like know more about the specifics of how draftsman interacts with Factorio, 
read further [here].

If you're interested in draftsman and want to try it for yourself, follow the 
[quickstart guide]. If instead you first want to get a feel for what draftsman 
looks and feels like, [take a look at some examples].

By loading Factorio's data dynamically, this allows users to create scripts that
work on *any* version of Factorio, with *any* mod list, no custom configuration
required. 


Mod configuration files 
(mod-list.json and mod-settings.dat) are also recognized during extraction, so
it really should be as simple as dropping the files into the folder.

"""

from draftsman._version import __version__, __version_info__
from draftsman._factorio_version import __factorio_version__, __factorio_version_info__
