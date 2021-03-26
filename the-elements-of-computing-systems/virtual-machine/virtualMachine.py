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

from virtualMachineLibrary.py import VirtualMachineLibrary

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

  def translate(path):
    #files = getfilesname
    #files should be either a file or a list of file names, depending if the path is a dir

    # for every vile in files
    # clean
    # translate (parse)
    # truncate and continue
    return 0

  def parse_file(input_file_name):
    output_file_name = input_file_name.split(".")[0] + ".asm"

    with open(input_file_name, 'r') as input_file, open(output_file_name, 'w') as output_file:
      instructions = input_file.readlines()
      output_file.seek(0)

      for line in instructions:
        instruction_structure = line.split()
        instruction = instruction_structure[0]
        
        if len(instruction_structure) == 1 and instruction != "return": # Stack arithmetic
          bytecode_instruction = get_arithmetic(instruction)

        elif instruction in ['pop', 'push']: # Memory access
          segment, index = instruction_structure[1], instruction_structure[2]
          bytecode_address = get_address_calculation(segment, index)
          bytecode_instruction_only = get_memory(instruction)
          
          # or vice-versa
          bytecode_instruction = bytecode_address.extend(bytecode_instruction_only)

        elif len(decoded_instruction) == 2: # Program flow
          # not implemented in v1
          bytecode_instruction = []
        else: # Function calling
          # not implemented in v1
          bytecode_instruction = []
        
        output_file.write(f"// {line}")
        for instruction in bytecode_instruction:
          output_file.write(instruction)

      input_file.truncate()
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


