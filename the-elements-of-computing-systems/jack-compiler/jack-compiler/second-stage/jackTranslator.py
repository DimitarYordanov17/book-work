# A jack translator (front-end). Jack code to Intermediate code. @DimitarYordanov17

# To run: python3 jackTranslator.py {path} {should standard library be added}
# (Final translator, capable of processing a full directory/.jack files, resulting in corresponding .vm files)

from jackTranslatorLibary import JackTranslatorLibrary
import os
import sys

class JackTranslator:
    """
    Main class, capable of processing a full directory, with .jack files, resutling in corresponding .vm files + ?OS (standard library) files
    """

    def translate(path, add_standard_library):
        """
        Translate a directory, resulting in len(path .jack files) .vm files
        """

        return 0

    def clean(input_file_name):
    	"""
		Clean a .jack file - remove comments and whitespaces
    	"""


    	return 0