#!/usr/bin/python3

#Take the provided data that is in CSV format and provide a command line tool that does the following:
#·        with no parameters other than the file name, produce a JSON version of the CSV file with the JSON objects separated by area code
#·        provide for optional parameters that:
#o   convert the file from CSV to XML (instead of JSON)
#o   returns a file that only contains JSON objects defined by a value associated within a certain field (e.g. LastName=Stanford)
#o   allows for a way to rename the new output file
#·        prove that it works
#·        it should work with other predictable problems with the data. (e.g. different Phone Number formatting, missing First Name, etc.)

#====
# Imports
#====
import argparse
import csv
import json
import phonenumbers
import re
import sys

from collections import defaultdict
from dicttoxml import dicttoxml
from os import path

#-----VARIABLES-----
json_dict = defaultdict(list)

#-----SET UP ARG PARSER-----
parser = argparse.ArgumentParser(description='Convert a CSV file into JSON (default) or XML')
parser.add_argument("name", help="Filename (with path if not in same directory as current session) of CSV file to import.")
parser.add_argument("-txl", "--toxml", help="Convert to XML (accepts true or false")
parser.add_argument("-of", "--outputfile", help="Filename of rewritten JSON or XML file (defaults to current filename/path).")
parser.add_argument("-se", "--searchelement", help="Search for only elements that have a particular value (for instance, 'Last Name=Smith' to find all records with a last name of Smith).")

args = parser.parse_args()
arguments = {}
filename = args.name

# Check here to see if we have an outputfile option. If we do, we need to use it as our output filename and path.
if args.outputfile is not None:
	# We have an outputfile
    testpath = args.outputfile
else:
	# We do not have an outputfile
    testpath = args.name

# Get the OS specific path for our output.    
full_path = path.realpath(testpath)
# Get the filename's length at the end of the path.
filename_length = len(path.basename(testpath))
# Get just the path (without the filename)
just_path = full_path[:-filename_length]
# Get just the filename that we're using to name our outputfile
pure_name = path.splitext(path.basename(full_path))[0]

#-----Check if we're searching-----
if args.searchelement is not None:
	# Make sure that they've formatted the search correctly.
    if "=" not in args.searchelement:
        print ("The search element function takes a row and a value, separated by an equals sign. Example: LastName=Smith")
        sys.exit(1)
    else:
		# Split search term apart from the search value
        splitstring = args.searchelement.split("=")
        if not splitstring[0]:
            print ("The search row must be defined. Please run this program with the -h flag to see example.")
            sys.exit(1)
        if not splitstring[1]:
            print ("The search string must be defined. Please run this program with the -h flag to see example.")
            sys.exit(1)
        search_row = splitstring[0]
        search_value = splitstring[1]

#-----Main function-----

try:
    # Get the phone number for each element. Separate out the area code. If there is no area code, group the record into a special category. Detect international numbers.
    # Note that if there is an international number, we're going to put it into its own bucket since there's no clear guideline on how to derive an area code from an
    # arbitrary country's number.
    
    # Open the file path that we've been given and iterate through the rows
    with open(filename, 'r') as file:
		# Don't leave anything to chance. We know the format the CSV is going to be in. Read it in and set our own header categories rather than trusting that this information
		# is going to be present on the first line.
        rows = csv.DictReader(file, fieldnames=("First Name", "Last Name", "Gender", "Phone Number", "ID", "Eye Color"))
        for row in rows:
            try:
				# Now just in case the first row (or any row) contains our headers, throw them away. We could check for more than just First Name, but for now we won't.
                if row['First Name'] == "First Name":
                  continue
                if args.searchelement is not None:
					# We're searching. If the search term that the user gave us matches the search value, we want to include it in our list. Otherwise, we throw this
					# row away.
                    if row[search_row] != search_value:
                        continue
                        
                # Cheap and dirty way to detect how we should parse the phone number. If we get a prefix code of '+' then phonenumbers can pick up its format from the
                # full string. If we don't have a '+' in the number, we need to tell the library how to parse the number. Since most of our data is going to be coming
                # in US format, we'll default to the US parsing.
                #
                # To make this more bulletproof, we could do explicit checks for more countries' formats (like great britain).
                if "+" not in row['Phone Number']:
                  phone_number = phonenumbers.parse(row['Phone Number'], "US")
                else:
                  phone_number = phonenumbers.parse(row['Phone Number'], None)
                
                # We now have a phonenumber object. Check to see if it's a valid phone number. If it isn't, we put it into a special bucket called 'bad_phone_numbers'.
                # We could also just throw away the row that has a bad phone number, but I'm going to err on the side of caution and retain the data in our output.
                if phonenumbers.is_valid_number(phone_number):
					# If the phone number has been parsed into US format, we'll have a three-digit area code surrounded by parens. If it is, we need to tease out
					# the three numbers between parens as our area code.
                    if "(" in phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.NATIONAL):
						# Do a regular expression w.capture group to get the area code.
                        area_code = re.search(r'\((.*?)\)',phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.NATIONAL)).group(1)
                        # make sure area code is 3 numeric digits
                        if len(area_code) == 3:
                            json_dict[area_code].append(row)
                        else:
							# Something weird happened with the area code. Create a special bucket for this outcome.
                            json_dict["unsorted_phone_numbers"].append(row)
                    else:
						# This is an international number. Toss this into the aforementioned international phone numbers bucket.
                        json_dict["international_phone_numbers"].append(row)
                else:
					# Not a valid phone number?  Put it into our special bad phone numbers bucket.
                    json_dict["bad_phone_numbers"].append(row)
                  
            except Exception as e:
                print (e)

        # Are we dumping this as XML or JSON? Test our optional toxml argument to see.
        if not args.toxml == "true":
            output_path = just_path + pure_name + ".json"
            output_data = json.dumps(json_dict)
        else:
            output_path = just_path + pure_name + ".xml"
            output_data = dicttoxml(json_dict).decode('ascii')

        # Write out file
        try:
            output_file = open(output_path, 'w')
            output_file.write(output_data)
            output_file.close()
        except Exception as output:
            print ("File could not be written. Please make sure that" + output_path + " is valid.")
except Exception as e:
    print ("File could not be opened. Please check file path for correct spelling.")
    sys.exit(1)
