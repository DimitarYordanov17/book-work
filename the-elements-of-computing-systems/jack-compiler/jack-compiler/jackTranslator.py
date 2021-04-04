# A jack translator (front-end). Jack code to Intermediate code. @DimitarYordanov17

# To run: python3 jackTranslator.py {path} {should standard library be added}

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
