# A library file containing Jack Standard Library function declarations and methods used to work with them. @DimitarYordanov17

import re

class JackStandardLibrary:
    """
    Main class to work with

    Standard library raw:
    Raw text from the book

    Standard library formatted:
    class_name: {function_name1: [function_kind, function_type, function_parameter_list], function_name2: [function_kind, function_type, function_parameter_list]}
    """
    
    standard_library_raw = open('jackStandardLibraryRaw.txt', 'r').read()
    standard_library_formatted = JackStandardLibrary.construct_formatted_library()

    def construct_formatted_library():
        """
        Format the raw library text into segment dictionaries
        """

        return 0
