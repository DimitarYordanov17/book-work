# A bytecode library for the VM code > Hack machine language translation. @DimitarYordanov17


class VirtualMachineLibrary:
  '''
  Main class to map the Virtual Machine intermediate language to Hack machine language
  '''

  def _get_primary(operation, a=None, b=None, treat_b_as_pointer=True):
    '''
    Define primary operations, which are going to be main building 'blocks' of higher (arithmetic/memory) instructions
    '''

    bytecode_dictionary = {
      "sp++": ["@SP", "M=M+1"],
      "sp--": ["@SP", "M=M-1"],
    }

    if operation == "*a=*b":
      load_b_into_d = [f"@{b}", "D=M"]

      if treat_b_as_pointer:
        load_b_into_d.insert(1, "A=M")

      load_d_into_a = [f"@{a}", "A=M", "M=D"]
      load_b_into_a = load_b_into_d + load_d_into_a

      return load_b_into_a

    else:
      return bytecode_dictionary[operation]

  def get_arithmetic(instruction, total_instructions):
    '''
    Returns bytecode for arithmetic instructions
    add | x + y
    sub | x - y
    neg | - y
    eq  | x == y
    gt  | x > y
    lt  | y < x
    and | x && y
    or  | x || y
    not | !y
    '''
    direct_arithmetic_commands = {"add" : '+', "sub": '-', "and": '&', "or": '|'}
    conditional_arithmetic_commands = {"eq" : 'JEQ', "gt": 'JGT', "lt": 'JLT'} # I can just preppend 'J' to the type and .upper(), because they match, but the symmetry would be ruined
    unary_commands = ["neg", "not"]

    final_bytecode = []

    if instruction in direct_arithmetic_commands:
      final_bytecode.extend(VirtualMachineLibrary._get_primary("sp--")) # sp--
      final_bytecode.extend(["@SP", "A=M", "D=M"]) # D=*sp

      final_bytecode.extend(VirtualMachineLibrary._get_primary("sp--")) # sp--
      final_bytecode.extend(["@SP", "A=M", f"D=M{direct_arithmetic_commands[instruction]}D"]) # D=*sp (operand)  D

      final_bytecode.extend(["@SP", "A=M", "M=D"]) # *sp = D
      final_bytecode.extend(VirtualMachineLibrary._get_primary("sp++")) # sp++
      
    elif instruction in conditional_arithmetic_commands:
      final_bytecode.extend(VirtualMachineLibrary._get_primary("sp--")) # sp--
      final_bytecode.extend(["@SP", "A=M", "D=M"]) # D=*sp

      final_bytecode.extend(VirtualMachineLibrary._get_primary("sp--")) # sp--
      final_bytecode.extend(["@SP", "A=M", "D=M-D"]) # D=*sp -  D
      
      final_bytecode.extend([f"@{total_instructions + 17}", f"D;{conditional_arithmetic_commands[instruction]}"]) # @WRITENONE, jump if the corresponding condition matches with D's (x-y) value

      final_bytecode.extend(["@SP", "A=M", "M=0"]) # (WRITEZERO) block, *sp=0 (false)
      final_bytecode.extend([f"@{total_instructions + 20}", "0;JMP"]) # Jump instantly to sp++ part, skipping write -1
      
      final_bytecode.extend(["@SP", "A=M", "M=-1"]) # (WRITENONE) block, *sp=-1 (true)

      final_bytecode.extend(VirtualMachineLibrary._get_primary("sp++")) # sp++

    else: # unary command
      final_bytecode.extend(VirtualMachineLibrary._get_primary("sp--")) # sp--

      final_bytecode.extend(["@SP", "A=M", "D=M"]) # D=*sp
        
      if instruction == "not":
        final_bytecode.extend(["@SP", "A=M", "M=!D"]) # *sp = !D
      else:
        final_bytecode.extend(["@SP", "A=M", "M=-D"])

      final_bytecode.extend(VirtualMachineLibrary._get_primary("sp++")) # sp++

    return final_bytecode

  def get_memory(instruction):
    '''
    Returns the full memory access bytecode, which consists of:
    1. Loading address calculation in R13
    2. Decrementing SP, if pop else saving R13's content into current SP available location
    3. Saveing SP value in R13, if pop else incrementing SP
    '''

    instruction_structure = instruction.split()
    instruction_type = instruction_structure[0]
    segment = instruction_structure[1]
    index = instruction_structure[2]
    
    calculated_address_bytecode = VirtualMachineLibrary._get_address_calculation(segment, index)

    if instruction_type == "push":
      treat_b_as_pointer = segment != "constant" # If we don't have a constant segment, then b (R13 in this case) must be treated as a pointer

      save_R13_into_stack_bytecode = VirtualMachineLibrary._get_primary("*a=*b", a="SP", b="R13", treat_b_as_pointer=treat_b_as_pointer)
      increment_sp = VirtualMachineLibrary._get_primary("sp++")

      return calculated_address_bytecode + save_R13_into_stack_bytecode + increment_sp

    else:
      decrement_sp = VirtualMachineLibrary._get_primary("sp--")
      save_stack_into_R13 = VirtualMachineLibrary._get_primary("*a=*b", a="R13", b="SP")

      return calculated_address_bytecode + decrement_sp + save_stack_into_R13

  def _get_address_calculation(segment, index):
    '''
    Returns bytecode that loads address calculation (segment base address + index) in R13 
    '''

    if segment == "constant":
      load_bytecode = [f"@{index}", "D=A"]
    else:
      load_bytecode = [f"@{VirtualMachineLibrary._get_symbolic_symbol(segment)}", "D=M", f"@{index}", "D=D+A"]
    
    full_address_bytecode = load_bytecode + ["@R13", "M=D"]
    return full_address_bytecode

  def _get_symbolic_symbol(segment):
    '''
    Returns Hack symbolic symbol equivalents
    '''
    bytecode_dictionary = {
      "local"   :    'LCL',
      "argument":    'ARG',
      "this"    :    'THIS',
      "that"    :    'THAT',
    }

    try: 
      return bytecode_dictionary[segment]
    except: # If the segment is not available, it means that it is most likely a variable, so just return it
      return segment
   
  def get_function(instruction):
    '''
    Not implemented in v1
    '''
    return 0

  def get_flow(instruction):
    '''
    Not implemented in v1
    '''
    return 0
