# A virtual machine translator. Intermediate code (supplied by a to be implemented compiler) -> Hack machine language. @DimitarYordanov17

# In the book, the main architecture of the VM translator consists
# of two modules - a Parser and a CodeWriter.
# In my case, I am thinking about doing it differently (just like the assembler) - 
# I will make a separate file (library) and access it
# whenever I need to, instead of using different modules.
# I will create a main class, in which I will still make the parser and writer functionalities
# but in the form of methods, which will use different methods too.
# For example, in the library file, I might include the usual syntax for an
# add instruction, so this file can stay clean (easier to scale later).
# I will implement the memory and stack arithmetic operations and later on - program flow and functions

from virtualMachineLibrary import VirtualMachineLibrary
import os
import sys

class VirtualMachineTranslator:
  """
  To be implemented
  Do something like this:
  1. For every file:
  1.1. Clean (comments, use already built function)
  1.2. Iterate through every line
  1.3. Fetch every instruction (identify command, arguments...)
  1.4. Make a request to the library, meaning that, get default assembly code
  for push, and eventually make an address calculation request.
  1.5. Write to file
  """

  def translate(input_file_name): 
    output_file_name = input_file_name.split(".")[0] + ".asm"
    os.system(f"cp {input_file_name} {output_file_name}")
    VirtualMachineTranslator.clean(output_file_name)
    VirtualMachineTranslator.parse_file(output_file_name)

  def parse_file(output_file_name):
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
          bytecode_instruction = VirtualMachineLibrary.get_memory(line)
          
        elif len(instruction_structure) == 2: # Program flow
          # not implemented in v1
          pass
        else: # Function calling
          # not implemented in v1
          pass
        
        output_file.write(f"// {line}")
        for instruction in bytecode_instruction:
          total_instructions += 1
          output_file.write(instruction + '\n')

      output_file.truncate()

    # input file is an .vm format, we should make a new .asm file
    # load file
    # iterate through every instruction
    # write comment
    # decode
    # get instruction and argument bytecode
    # write to output fil
    
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
