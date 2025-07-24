.. py:currentmodule:: draftsman.environment.script

.. draftsman_command_line_tool

:py:mod:`~draftsman.environment.script`
=======================================

Primary console entry point for the ``draftsman`` command line tool. 
Enter ``draftsman -h`` to get a list of all commands that the tool supports, with a plain-text description of their function:

.. code-block:: text

    > draftsman -h
    usage: draftsman [-h] [-p GAME_PATH] [-m MODS_PATH] [-v] {list,mod-settings,enable,disable,version,factorio-version,update} ...

    A command-line utility for reporting and manipulating Draftsman's environment.

    positional arguments:
    {list,mod-settings,enable,disable,version,factorio-version,update}
                            Operation:
        list                Lists information about all mods in the current environment.
        mod-settings        Displays all custom mod settings in `mod-settings.dat`, if present.
        enable              Enables a mod or mods.
        disable             Disables a mod or mods.
        version             Displays the current Draftsman version.
        factorio-version    Displays or sets the current version of Factorio's data.
        update              Updates Draftsman's environment by emulating Factorio's data lifecycle.

    options:
    -h, --help            show this help message and exit
    -p GAME_PATH, --game-path GAME_PATH
                            The path to the data folder of the game; defaults to: 
                            `[python_install]/site-packages/draftsman/factorio-data`. 
                            If you own the game, you can pass in the folder where Factorio is installed, 
                            which will give you the ability to extract asset data in addition to prototype 
                            data.
    -m MODS_PATH, --mods-path MODS_PATH
                            The path to search for (user) mods; defaults to 
                            `[python_install]/site-packages/draftsman/factorio-mods`.
    -v, --verbose         Report additional information to stdout when available.

All commands have the ``GAME_PATH`` and ``MODS_PATH`` arguments (which allow you to specify where Draftsman should look for it's data) and the ``verbose`` argument for printing additional useful information.
Each command also has it's own ``-h``, which allows you to inspect each one in more detail.

``draftsman list``
------------------

Lists all detected mods at the specified game and mod paths, sorted alphabetically by mod name.

.. code-block:: text

    > draftsman list   
     ✓ (dir) base               2.0.61
     ✓ (dir) core                    -
     ✓ (dir) elevated-rails     2.0.61
     ✓ (dir) quality            2.0.61
     ✓ (dir) space-age          2.0.61

From left to right:

* A check mark indicates that the mod is *enabled*, wheras an empty space would indicate that it's *disabled*. 
* If the data is located in a directory it will print the string ``(dir)``; if the file is compressed inside of an archive (typical for mods) it will print ``(zip)``.
* Following this is the internal name of the "mod", although in this case "mod" also includes the game's data itself; hence why the "mods" ``base`` and ``core`` are in this list. This is simply a peculiarity of how the game abstracts it's internal data.
* Finally, the mod version is also printed. Only the ``core`` mod is special and exempt from this requirement, instead printing a dash to indicate no value.

Sometimes, you can have multiples of the same mod with different versions. In this case, each mod version is displayed, with a horizontally-spanning arrow to indicate that it is a duplicate of the name above:

.. code-block:: text

     ✓ (zip) Krastorio2Assets                                     2.0.0
       (zip) ├──────────────>                                     1.2.3
       (zip) └──────────────>                                     1.2.2

Here, there are three different versions of ``Krastorio2Assets``.
Take note both that the sublist is sorted in descending version, and the only mod in this list indicated as active is the latest version.
This is to indicate that the mod specified as enabled will be the one which Draftsman (and indeed Factorio) will pick when running the data lifecycle.
If there are two copies of the exact same mod with the exact same version, but one is a folder and the other is an archive, the folder will be preferred.

Using the verbose ``-v`` option will also display exactly where the mods are located on disk, alongside a more explicit table view:

.. code-block:: text

    > draftsman -v list
    on? ┃ type  ┃ name           ┃ version ┃ location
    ━━━━╋━━━━━━━╋━━━━━━━━━━━━━━━━╋━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     ✓  ┃ (dir) ┃ base           ┃  2.0.61 ┃ D:/SourceCode/repos/Python/factorio-draftsman/draftsman/factorio-data/base
     ✓  ┃ (dir) ┃ core           ┃       - ┃ D:/SourceCode/repos/Python/factorio-draftsman/draftsman/factorio-data/core
     ✓  ┃ (dir) ┃ elevated-rails ┃  2.0.61 ┃ D:/SourceCode/repos/Python/factorio-draftsman/draftsman/factorio-data/elevated-rails
     ✓  ┃ (dir) ┃ quality        ┃  2.0.61 ┃ D:/SourceCode/repos/Python/factorio-draftsman/draftsman/factorio-data/quality
     ✓  ┃ (dir) ┃ space-age      ┃  2.0.61 ┃ D:/SourceCode/repos/Python/factorio-draftsman/draftsman/factorio-data/space-age

Here you can see that the script is pulling data from the local ``factorio-data`` installation (the default location).

``draftsman mod-settings``
--------------------------

Decodes the ``mod-settings.dat`` file and allows you to view it's key-value pairs, organized by setting category:

.. code-block:: text

    > draftsman --mods-path %APPDATA%/Factorio/mods mod-settings         
    STARTUP:
            nixie-tube-slashed-zero: True
            bobmods-inserters-long1: True
            bobmods-inserters-long2: True
            bobmods-inserters-more2: True
    RUNTIME-GLOBAL:
            helmod_debug_solver: False
            helmod_user_cache_step: 100
            helmod_display_all_sheet: False
            helmod_filter_translated_string_active: True
            helmod_filter_on_text_changed: False
            helmod_model_filter_factory: True
            helmod_model_filter_beacon: True
            helmod_model_filter_factory_module: True
            helmod_model_filter_beacon_module: True
            helmod_hidden_panels: False
            helmod_display_hidden_column: 'None'
            nixie-tube-update-speed-alpha: 10
            nixie-tube-update-speed-numeric: 5
            recursive-blueprints-area: 'corner'
            recursive-blueprints-deployer-deploy-signal: 'zero'
            recursive-blueprints-logging: 'never'
    RUNTIME-PER-USER:
            helmod_display_ratio_horizontal: 0.85
            helmod_display_ratio_vertical: 0.8
            helmod_display_main_icon: True
            helmod_display_cell_mod: 'default'
            helmod_row_move_step: 5
            bobmods-inserters-button-enable: True
            bobmods-inserters-gui-position: 'right'
            bobmods-inserters-show-window: 'off'

If no file is found, the script early-exits, specifiying where it couldn't find the desired file:

.. code-block:: text

    > draftsman mod-settings
    No `mod-settings.dat` file found at 'D:\SourceCode\repos\Python\factorio-draftsman\draftsman\factorio-mods'

Currently, there are no faculties to modify these values externally via this script, although adding this functionality would be trivial; see :py:meth:`~draftsman.environment.mod_settings.write_mod_settings`.

``draftsman enable/disable``
----------------------------

Enables or disables a mod or mods. For example, if you wanted to disable the Factorio 2.0 DLC mods, simply specify the name of each one separated by spaces:

.. code-block:: text

    > draftsman disable space-age quality elevated-rails
    > draftsman list
    ✓ (dir) base               2.0.61
    ✓ (dir) core                    -
      (dir) elevated-rails     2.0.61
      (dir) quality            2.0.61
      (dir) space-age          2.0.61

Enabling is obviously the converse of this.
Both enable and disable also support the special keyword ``all``, which enables/disables every mod except for ``base`` and ``core``:

.. code-block:: text

    > draftsman --mods-path %APPDATA%/Factorio/mods enable all
    > draftsman --mods-path %APPDATA%/Factorio/mods list
    ✓ (dir) base                                                2.0.61
    ✓ (dir) core                                                     -
    ✓ (dir) elevated-rails                                      2.0.61
    ✓ (dir) quality                                             2.0.61
    ✓ (dir) space-age                                           2.0.61
    ✓ (zip) 0FactorioExtended-Plus-Layout                        1.1.5
    ✓ (zip) aai-containers                                       0.3.1
    ✓ (zip) aai-industry                                         0.6.5
    ✓ (zip) aai-loaders                                          0.2.5
    ✓ (zip) aai-signal-transmission                              0.5.0
    ...
    etc
    ...
    ✓ (zip) Squeak Through                                       1.8.2
    ✓ (zip) StatsGui                                             1.6.1
    ✓ (zip) subspace_storage                                   1.99.20
    ✓ (zip) textplates                                           0.7.2
      (zip) └────────>                                          0.6.10
    ✓ (zip) Todo-List                                           19.9.0
    ✓ (zip) TrainGroups                                          1.4.3
    ✓ (zip) Ultracube                                            0.6.4
      (zip) ├───────>                                            0.5.6
      (zip) └───────>                                           0.3.11

Mods ``base`` and ``core`` can still be enabled/disabled using these commands, as long as you do so explicitly:

.. code-block:: text

    > draftsman disable base core
    > draftsman list
      (dir) base               2.0.61
      (dir) core                    -
    ✓ (dir) elevated-rails     2.0.61
    ✓ (dir) quality            2.0.61
    ✓ (dir) space-age          2.0.61

If you need a to specify a mod's name that includes whitespace, use quotes:

.. code-block:: text

    > draftsman enable "Squeak Through"

``draftsman version``
---------------------

Simply prints the current Draftsman version. Useful for logging/pretty printing.

.. code-block:: text

    > draftsman version
    Draftsman 3.0.0

``draftsman factorio-version``
------------------------------

Reads or writes the version of the Draftsman-installed Factorio version.

.. code-block:: text

    > draftsman factorio-version
    Factorio 2.0.60

.. NOTE::

    The version that this command outputs is the git tag of the ``factorio-data`` repository.
    The value that is internally stored and extracted is usually *one version ahead of this tag*:

    .. code-block:: python

        > draftsman factorio-version
        Factorio 2.0.60
        > python
        Python 3.12.10 (tags/v3.12.10:0cc8128, Apr  8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)] on win32
        Type "help", "copyright", "credits" or "license" for more information.
        >>> from draftsman.data import mods
        >>> mods.versions["base"]
        (2, 0, 61, 0)

    Keep this in mind when versioning your scripts.
    
In addition to viewing the current version, you can also update it to a different version:

.. code-block:: text

    > draftsman -v factorio-version 1.0.0
    Current Factorio version: 2.0.60
    Different Factorio version requested:
            (2.0.60) -> (1.0.0)
    Changed to Factorio version 1.0.0

.. NOTE:: 

    This command sets the git submodule version to the specified tag and checks it out, updating the data internal to that specific folder.
    This does not actually update *Draftsman's* data - that is taken care of by ``draftsman update``.
    If trying to update Draftsman's data to correspond with a new Factorio version, use these two commands sequentially.

You can also use the keyword ``latest`` to specify the most recent git tag:

.. code-block:: text

    > draftsman -v factorio-version latest
    Current Factorio version: 1.0.0
    Different Factorio version requested:
            (1.0.0) -> (2.0.60)
    Changed to Factorio version 2.0.60

This command is only intended to be used for managing the version of Factorio data which comes shipped alongside Draftsman.
That is, it will be unable to read or modify the version of your *regular* installation:

.. code-block:: text

    > draftsman --game-path D:/Steam/steamapps/common/Factorio/data factorio-version
    Traceback (most recent call last):
    File "<frozen runpy>", line 198, in _run_module_as_main
    File "<frozen runpy>", line 88, in _run_code
    File "C:\Users\tfsch\AppData\Roaming\Python\Python312\Scripts\draftsman.exe\__main__.py", line 7, in <module>
    File "D:\SourceCode\repos\Python\factorio-draftsman\draftsman\environment\script.py", line 193, in main
        repo = git.Repo(args.game_path)
            ^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\tfsch\AppData\Roaming\Python\Python312\site-packages\git\repo\base.py", line 289, in __init__
        raise InvalidGitRepositoryError(epath)
    git.exc.InvalidGitRepositoryError: D:\Steam\steamapps\common\Factorio\data

This functionality may be possible in the future, but currently is not supported.

``draftsman update``
--------------------

Runs the Factorio data lifecycle and extracts the data into a number of pickle files located in the ``draftsman/data`` directory.
Use this to update Draftsman's metadata any time the Factorio or mod configuration has been altered.

.. code-block:: text

    > draftsman update -h
    usage: draftsman update [-h] [-l] [--no-mods]

    Runs the Factorio data lifecycle using the data pointed to by `game_path`. All information that 
    Draftsman needs will be extracted into pickle files located in the draftsman/data/ folder in the 
    installation directory.

    options:
    -h, --help  show this help message and exit
    -l, --log   Display any `log()` messages to stdout; any logged messages will be ignored if this 
                argument is not set.
    --no-mods   Prevents user mods from loading even if they are enabled. Official mods made by Wube 
                (`quality`, `elevated-rails`, `space-age`) are NOT affected by this flag; those should 
                be manually configured with `draftsman enable|disable [official-mod]`

In addition to the universal ``GAME_PATH``, ``MODS_PATH``, and ``verbose``, update supports a ``--no-mods`` flag which allows you to quickly ignore any non-official mod, if you quickly want to reduce your configuration to a vanilla state:

.. code-block:: text

    > draftsman -v update --no-mods
    Discovering mods...

    ✓ (dir) base               2.0.61
    ✓ (dir) core                    -
    ✓ (dir) elevated-rails     2.0.61
    ✓ (dir) quality            2.0.61
    ✓ (dir) space-age          2.0.61

    Determining dependency tree...

    base
            core
    elevated-rails
            base >= 2.0.0
    quality
            base >= 2.0.0
    space-age
            base >= 2.0.0
            elevated-rails >= 2.0.0
            quality >= 2.0.0

    Load order:
    ['core', 'base', 'elevated-rails', 'quality', 'space-age']

    SETTINGS.LUA:
    SETTINGS-UPDATES.LUA:
    SETTINGS-FINAL-FIXES.LUA:
    DATA.LUA:
            mod: core
            mod: base
            mod: elevated-rails
            mod: quality
            mod: space-age
    DATA-UPDATES.LUA:
            mod: base
            mod: quality
            mod: space-age
    DATA-FINAL-FIXES.LUA:

    Extracting data...

    Extracted mods...
    Extracted entities...
    Extracted equipment...
    Extracted fluids...
    Extracted instruments...
    Extracted items...
    Extracted modules...
    Extracted planets...
    Extracted qualities...
    Extracted recipes...
    Extracted signals...
    Extracted tiles...

    Update finished.
    hella slick; nothing broke!

All of the individual functionality of the above commands are abstracted out into Python methods, which can be imported from their corresponding files in :py:mod:`draftsman.environment`.