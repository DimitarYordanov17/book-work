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
# I will implement the memory and stack arithmetic operations and later on - branching and functions

class VirtualMachineTranslator:
  """
  To be implemented
  """
