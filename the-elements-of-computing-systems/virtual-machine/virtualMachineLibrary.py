# A bytecode library for the VM code > Hack machine language translation. @DimitarYordanov17


class VirtualMachineLibrary:
  '''
  Main class to map the Virtual Machine intermediate language to Hack machine language
  '''

  def _primary(operation):
    '''
    Define primitive operations, which are going to be main building 'blocks' of higher (arithmetic/memory) instruction
    '''
    # TODO: Add full primitive operations
    bytecode_dictionary = {
    "sp++": [...],
    "sp--": [...],
    ...
    }

    return bytecode_dictionary[operation]

  def get_arithmetic(instruction):
    '''
    Returns bytecode for arithmetic instructions
    '''
    # TODO: Add full commands

  def get_memory(instruction, segment, index):
    '''
    Makes a call to calculate address and returns full memory bytecode
    '''
    # TODO: Add full commands

  def _get_address_calculation(segment, index):
    '''
    Returns bytecode segment + index calculation
    '''
    # TODO: Add address calculation
    
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
