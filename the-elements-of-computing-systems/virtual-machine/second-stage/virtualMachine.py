# A virtual machine translator. Intermediate code (supplied by a to be implemented compiler) -> Hack machine language. @DimitarYordanov7
# To run: python3 virtualMachine.py {your .vm file}
# (This file is the second stage translator, capable of processing a whole directory and handling functional and conditional instructions)

from virtualMachineLibrary import VirtualMachineLibrary
import os
import sys


class VirtualMachineTranslator:
    """
    Main class, capable of processing a full directory, with .vm files, resulting in one .asm file
    """

    def translate_files(path):
        """
        Translate all .vm files in path
        """

        if '.' in path:  # We have a file
            output_file_name = path.split(".")[0] + ".asm"
            os.system(f"cp {path} {output_file_name}")
            VirtualMachineTranslator.clean(output_file_name)
            VirtualMachineTranslator.parse_file(output_file_name)

        else:  # We have a directory
            vm_files = []

            for root, dirs, files in os.walk(path):

                for file_name in files:
                    file_extension = file_name.split('.')[1]

                    if file_extension == 'vm':
                        vm_files.append(file_name)

            # Try recursion?
            for vm_file in vm_files:
                VirtualMachineTranslator.translate(vm_file)

    def parse_file(input_file_name):
        """
        Parse every instruction and write the requested and further translated equivalent
        """

        with open(input_file_name, 'r+') as input_file:
            total_instructions = 0
            instructions = input_file.readlines()
            input_file.seek(0)

            for line in instructions:
                instruction_structure = line.split()
                instruction = instruction_structure[0]

                bytecode_instruction = []

                if len(instruction_structure) == 1 and instruction != "return":  # Stack arithmetic
                    bytecode_instruction = VirtualMachineLibrary.get_arithmetic(instruction, total_instructions)

                elif instruction in ['pop', 'push']:  # Memory access
                    bytecode_instruction = VirtualMachineLibrary.get_memory(line, input_file_name.split('.')[0])

                elif len(instruction_structure) == 2:  # Program flow
                    # not implemented in first-stage
                    pass
                else:  # Function calling
                    # not implemented in first-stage
                    pass

                input_file.write(f"// {line}")

                for instruction in bytecode_instruction:
                    total_instructions += 1
                    input_file.write(instruction + '\n')

            input_file.truncate()

    def clean(input_file):
        """
        Remove unnecesary whitespaces and comments
        """

        with open(input_file, "r+") as f:
            lines = f.readlines()
            f.seek(0)
            for line in lines:
                if line != '\n':
                    if "//" in line:
                        line_elements = line.lstrip().split("//")
                        if line_elements[0]:
                            f.write(line_elements[0].rstrip() + '\n')
                    else:
                        f.write(line)
            f.truncate()


VirtualMachineTranslator.translate_files(sys.argv[1])
