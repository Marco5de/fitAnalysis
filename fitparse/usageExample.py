from fitparse import FitFile,FitParseError
import sys

file = open("ParsedFitOut.txt","w")

try:
    fitfile = FitFile("file.fit")
    fitfile.parse()
except FitParseError as e:
    print("Error parsing .FIT file")
    sys.exit(1)

# Get all data messages that are of type record
#fitfile.get_messages('record') returns record info!
for record in fitfile.get_messages():

    # Go through all the data entries in this record
    for record_data in record:

        # Print the records name and value (and units if it has any)
        if record_data.units:
            print(" * %s: %s %s" % (record_data.name, record_data.value, record_data.units,))
            file.write(" * %s: %s %s\n" % (record_data.name, record_data.value, record_data.units,))
        else:
            print(" * %s: %s" % (record_data.name, record_data.value))
            file.write(" * %s: %s\n" % (record_data.name, record_data.value))
    print("\n")
    file.write("\n")
file.close()