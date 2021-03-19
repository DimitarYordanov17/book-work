// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

// Initialize the result register with 0 to escape zero multiplication fallacy
  @0
  D=A
  @R2
  M=D

(LOOP)
  // If all multiplication has been done, end multiplication loop
  @R1
  D=M
  @END
  D;JEQ

  // Add R0 to R2
  @R2
  D=M
  @R0
  D=D+M
  @R2
  M=D
  
  // Decrement R1
  @1
  D=A
  @R1
  D=M-D
  M=D

  // Jump back to make another round of multiplication
  @LOOP
  0;JMP

(END) // Of course, what is the best way to terminate a program if it is not an infinite loop
  @END
  0;JMP
