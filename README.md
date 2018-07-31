# convertcsv
usage: csv2json.py [-h] [-txl TOXML] [-of OUTPUTFILE] [-se SEARCHELEMENT] name

Convert a CSV file into JSON (default) or XML

positional arguments:
  name                  Filename (with path if not in same directory as
                        current session) of CSV file to import.

optional arguments:

  -h, --help            show this help message and exit

  -txl TOXML, --toxml TOXML

                        Convert to XML (accepts true or false

  -of OUTPUTFILE, --outputfile OUTPUTFILE

                        Filename of rewritten JSON or XML file (defaults to

                        current filename/path).

  -se SEARCHELEMENT, --searchelement SEARCHELEMENT

                        Search for only elements that have a particular value

                        (for instance, 'Last Name=Smith' to find all records

                        with a last name of Smith).
