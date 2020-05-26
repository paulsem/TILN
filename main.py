from TimeEx.GUI import interface
from TimeEx.PARSARE import proiect

print("Don't forget to run:\n\tpip install -r requirments.txt")

# This function works only with the file: input/extract.txt !
# Sutimev = True => generates the SUTime Dictionary (Takes around 3 minutes!); To be used only when changing the input!
#
#           !!! Don't forget to add the 300 MB file: stanford-corenlp-3.9.2-models.jar !!!
#
# Sutimev = False => takes the already saved SUTime Dictionary from "tmp/dict_export_sutime.txt"
proiect.compare(sutimev=False)

# Run the main application
my_gui = interface.TextApp()
