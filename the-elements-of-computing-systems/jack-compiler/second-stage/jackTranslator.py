# A jack translator (front-end). Jack code to Intermediate code. @DimitarYordanov17

# To run: python3 jackTranslator.py {path}

from jackTranslatorLibrary import JackTranslatorLibrary
import os
import sys


class JackTranslator:
    """
    Main class, capable of processing a full directory, with .jack files, resulting in corresponding .vm files files
    """


    def translate(path):
        """
        Translate a directory/file, .jack -> .vm
        """
        
        jack_files = []

        for root, dirs, files in os.walk(path):
            for file_name in files:
                if ".jack" in file_name:
                  jack_files.append(file_name)
        
        for jack_file_name in jack_files:
            output_file_name = jack_file_name.split(".")[0] + ".vm"
            
            vm_code = JackTranslatorLibrary.translate_file(jack_file_name)

            with open(output_file_name, 'w') as output_file:
                for line in vm_code:
                    output_file.write(line)


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


JackTranslator.translate(sys.argv[1])
