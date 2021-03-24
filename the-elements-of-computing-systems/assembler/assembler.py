# A Python assembler for the Hack machine language. @DimitarYordanov17
# The whole idea is to make one main Assembler class, which implement the following functionalities, in order to sucessfully translate .asm (Hack assembly) to .hack (Hack machine code) programs
# 0. Remove unnecesary whitespaces and comments
# 1. Symbolic preprocessor
#   1.1. Jump preprocessor
#   1.2. Variables preprocessor
# 2. Parser
# 3. Code translator

from libAssembler import AssemblerLibrary

class Assembler:
  '''
  Main class, with no need of initialization, which offers an assemble functionality, to convert .asm to .hack files
  '''

  def assemble(path: str):
    '''
    Make use of class methods to translate a file
    '''
    # Get main file
    program_asm  = open(path, 'r')
    program_asm_list = program_asm.readlines()

    # Make an intermediate file for the symbolic and cleaner preprocessor
    intermediate_asm_name = "program_intermediate.asm"
    intermediate_asm = open("program_intermediate.asm", 'w')
    intermediate_asm.write(program_asm.read())
    
    # 0. Use cleaner preprocessor
    Assembler.clean(intermediate_asm_name)

    # 1.Apply symbolic preprocessor to the intermediate file
    Assembler.symbolic_preprocessor(intermediate_asm)
    
    # 2. Parse the intermediate_asm file
    Assembler.parse(intermediate_asm)
    
    # Create a new .hack file which is ready to be parsed from the cleaned and symbolically preprocessed intermediate_asm file
    program_hack_name = path.split('.')[0] + ".hack"
    program_hack = open(program_hack_name, 'w')

    # 3. Translate the well-formated intermediate_asm to machine code
    Assembler.translate(intermediate_asm, pogram_hack)

  def symbolic_preprocessor(file_asm):
    '''
    1. Construct a jump and variables  symbolic table
    2. Translate via the symbolic table
    '''
    symbolic_table = dict()
    variables = 0

    with open(file_asm, "r+") as f:
      lines = f.readlines()
      
      # Build jump symbolic table part
      for index, line in enumerate(lines):
        if line[0] == "(":
          symbolic_table[line[1:-2]] = index - len(symbolic_table.keys())
      


      # Build registers symbolic table part
      for line in lines:
        if "@" in line:
          address = line[1:].strip()

          if (not address.isnumeric()) and (address not in symbolic_table.keys()):
            address_request = AssemblerLibrary.get_register(address)
            if address_request == "VARIABLE":
              symbolic_table[address] = 16 + variables
              variables += 1
            
    print(symbolic_table)

  def clean(file_asm):
    '''
    Remove unnecesary whitespaces and comments
    '''
    with open(file_asm, "r+") as f:
      lines = f.readlines()
      f.seek(0)
      for line in lines:
        spaceless_line = line.replace(" ", "").lstrip()

        if line != '\n':
            if "/" in spaceless_line:
              divided_line = spaceless_line.split("/")
              if divided_line[0] and divided_line[0] != "*":
                f.write(divided_line[0] + '\n')

            elif "*" not in spaceless_line:
              f.write(spaceless_line)
              
      f.truncate()

  def parse(file_asm):
    '''
    Prepare the file for the code translator - decode the instructions
    '''
    return 0

  def translate(file_asm):
    '''
    Translate a prepared file into Hack machine code
    '''
    return 0

Assembler.clean("Fill_test.asm")
Assembler.symbolic_preprocessor("Fill_test.asm")
