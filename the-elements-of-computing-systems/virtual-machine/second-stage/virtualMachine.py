# A virtual machine translator. Intermediate code (supplied by a to be implemented compiler) -> Hack machine language. @DimitarYordanov7
# To run: python3 virtualMachine.py {your .vm file}
# (This file is the second stage translator, capable of processing a whole directory and handling functional and conditional instructions)

from virtualMachineLibrary import VirtualMachineLibrary
import os
import sys

class VirtualMachineTranslator:
  """
  Main class, capable of processing a single .vm (intermediate code) file, which consist of only stack + memory instructions
  """

  def translate(input_file_name): 
    """
    Handle the step-by-step proccess of translating a file
    """

    output_file_name = input_file_name.split(".")[0] + ".asm"
    os.system(f"cp {input_file_name} {output_file_name}")
    VirtualMachineTranslator.clean(output_file_name)
    VirtualMachineTranslator.parse_file(output_file_name)

  def parse_file(output_file_name):
    """
    Parse every instruction and write the requested and further translated equivalent
    """

    with open(output_file_name, 'r+') as output_file:
      total_instructions = 0
      instructions = output_file.readlines()
      output_file.seek(0)

      for line in instructions:
        instruction_structure = line.split()
        instruction = instruction_structure[0]
        
        bytecode_instruction = []

        if len(instruction_structure) == 1 and instruction != "return": # Stack arithmetic
          bytecode_instruction = VirtualMachineLibrary.get_arithmetic(instruction, total_instructions)

        elif instruction in ['pop', 'push']: # Memory access
          bytecode_instruction = VirtualMachineLibrary.get_memory(line, output_file_name.split('.')[0])
          
        elif len(instruction_structure) == 2: # Program flow
          # not implemented in first-stage
          pass
        else: # Function calling
          # not implemented in first-stage
          pass
        
        output_file.write(f"// {line}")

        for instruction in bytecode_instruction:
          total_instructions += 1
          output_file.write(instruction + '\n')

      output_file.truncate()
    
  def clean(input_file):
    '''
    Remove unnecesary whitespaces and comments
    '''

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

VirtualMachineTranslator.translate(sys.argv[1])
