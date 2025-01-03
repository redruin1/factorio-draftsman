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
"""

from draftsman._version import __version__, __version_info__
from draftsman._factorio_version import __factorio_version__, __factorio_version_info__
