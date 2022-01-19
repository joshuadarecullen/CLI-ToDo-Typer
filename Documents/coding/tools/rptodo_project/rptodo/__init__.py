# Here, you start by defining two module-level names to hold the application’s name and version. Then you define a series of return and error codes and assign integer numbers to them using range(). ERROR is a dictionary that maps error codes to human-readable error messages.
"""Top-level package for RP To-Do."""
# rptodo/__init__.py

__app_name__ = "rptodo"
__version__ = "0.1.0"

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    ID_ERROR,
) = range(7)

ERRORS = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    ID_ERROR: "to-do id error",
}
