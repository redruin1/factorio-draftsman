# conftest.py


# @pytest.fixture(scope="session", params=["sqlite", "postgresql"])
# def draftsman_environment(request):
#     """A session-scoped fixture that provides a database connection."""
#     db_type = request.param
#     if db_type == "sqlite":
#         print(f"\nSetting up SQLite connection for session.")
#         # Simulate database connection setup
#         connection = f"SQLite_Connection_{db_type}"
#     elif db_type == "postgresql":
#         print(f"\nSetting up PostgreSQL connection for session.")
#         # Simulate database connection setup
#         connection = f"PostgreSQL_Connection_{db_type}"
#     yield connection
#     print(f"\nTearing down {db_type} connection for session.")

# @pytest.hookimpl()
# def pytest_sessionstart(session):
#     # Grab and populate the repo, making sure its a git repo we expect
#     draftsman_path = os.path.dirname(os.path.abspath(draftsman.__file__))
#     repo = git.Repo(draftsman_path + "/factorio-data")
#     repo.git.fetch()
#     assert (
#         repo.remotes.origin.url == "https://github.com/wube/factorio-data"
#     ), "Targeted repo is not `wube/factorio-data`"

#     tag_list = sorted([version_string_to_tuple(tag.name) for tag in repo.tags])
#     # Only select versions >= 1.0
#     tag_list = tag_list[tag_list.index((1, 0, 0, 0)):]

#     # Checkout version
#     repo.git.checkout(version_tuple_to_string(tag_list[0][:3]))

#     print(tag_list)

#     # Update my data
#     run_data_lifecycle()

#     # Now run tests
