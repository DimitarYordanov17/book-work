# A jack translator (front-end). Jack code to Intermediate code. @DimitarYordanov17

# To run: python3 jackTranslator.py {path}

from jackTranslatorLibrary import JackTranslatorLibrary
import os
import sys


class JackTranslator:
    """
    Main class, capable of processing a full directory, with .jack files, resutling in corresponding .vm files files
    """

    def translate(path, add_standard_library):
        """
        Translate a directory, resulting in len(path .jack files) .vm files
        """

        #TODO: write code :D

        return 0

    def _construct_xml(input_file_name):
        """
        Parses a single .jack file, resulting in a .xml file
        """

        output_file_name = input_file_name.split(".")[0] + ".xml"
        os.system(f"cp {input_file_name} {output_file_name}")

        JackTranslatorLibrary.clean(output_file_name)
        JackTranslatorLibrary.tokenize(output_file_name)

        JackTranslatorLibrary.parse_file(output_file_name)

        JackTranslatorLibrary.tabularize(output_file_name)