# revision_history_experiment.py

"""
Testing related to a vanilla-adjacent method to store git-style diffs with 
ctime/mtime support. Spawned from a discussion on the Technical Factorio Discord
server.

Works as long as the entities remain tile ghosts; once they're placed creating
a new blueprint from the entities loses specified tag information. A mod would
likely have to be developed alongside to make this persistent, but that is 
outside the scope of Draftsman.
"""

from draftsman.blueprintable import Blueprint

from datetime import datetime


def main():
    # Export blueprint with custom data to Factorio
    bp = Blueprint()
    bp.entities.append("transport-belt")
    bp.entities[0].tags["git_history"] = {"creation": str(datetime.now())} # or whatever
    importable_string = bp.to_string()
    print(importable_string)

    # If read back, extract such data from blueprint string
    bp = Blueprint(importable_string)
    if "git_history" in bp.entities[0].tags:
        date = datetime.fromisoformat(bp.entities[0].tags["git_history"]["creation"])
        print(date)



if __name__ == "__main__":
    main()