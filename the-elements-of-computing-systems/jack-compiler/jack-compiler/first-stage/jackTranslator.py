# A jack translator (front-end). Jack code to Intermediate code. @DimitarYordanov17

# To run: python3 jackTranslator.py {path} {should standard library be added}
# (This is the first-stage translator which is capable of only tokenizing and parsing a .jack file/directory, resulting in XML file)

from jackTranslatorLibrary import JackTranslatorLibrary
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

    def construct_xml(input_file_name):
        """
        Parses a single .jack file, resulting in .xml file
        """
        output_file_name = input_file_name.split(".")[0] + ".xml"
        os.system(f"cp {input_file_name} {output_file_name}")
        JackTranslatorLibrary.clean(output_file_name)
        JackTranslatorLibrary.tokenize(output_file_name)
        #xml_code = JackTranslatorLibrary.parse_file(output_file_name)

        #with open(output_file_name, "w") as output_file:
        #   output_file.seek(0)
        #   for line in xml_code:
        #        output_file.write(line + '\n')


JackTranslator.construct_xml(sys.argv[1])
