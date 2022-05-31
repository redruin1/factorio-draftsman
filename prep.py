# prep.py

"""
Script to automatically perform testing, formatting, building and any other 
operation needed before distribution. Currently WIP.
"""

import coverage
import os
import subprocess
import unittest


def main():
    # Before this, we assume that the version is correctly incremented
    # Run black, format draftsman + test folders
    subprocess.run(["black", "draftsman"])
    subprocess.run(["black", "test"])

    # Before running testing, run the update script to reset to no mods
    # err = subprocess.run(["draftsman-update", "--no-mods"])
    # if err.returncode:
    #     print(err)
    #     return err

    # Run code coverage, fail if not 100%
    # cov = coverage.Coverage()
    
    # test_loader = unittest.TestLoader()
    # tests = test_loader.discover("test")
    # test_runner = unittest.TextTestRunner()
    # print(tests)
    
    # cov.start()

    # result = test_runner.run(tests)

    # cov.stop()
    # cov.save()
    # cov.report()
    # #f = open(os.devnull, "w")
    # print(cov.html_report())

    # Run tox, fail if tox failed at any point
    err = subprocess.run(["tox"])
    if err.returncode:
        print(err)
        return err

    # Run build
    # This doesn't work for some reason
    #subprocess.run(["python", "-m", "build", "."])
    # But this does
    os.system("python -m build .")


if __name__ == "__main__":
    main()