"""RP To-Do entry point script."""
# rptodo/__main__.py

from rptodo import cli, __app_name__

#  Providing a value to prog_name ensures that your users get the correct app name 
# when running the --help option on their command line.
def main():
    cli.app(prog_name=__app_name__)

if __name__ == "__main__":
    main()
