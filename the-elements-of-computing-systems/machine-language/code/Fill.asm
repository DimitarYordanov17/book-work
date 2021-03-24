// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// Removed unnecessary initialization
// Another way to optimize this is by making a single block - DRAWPIXEL
// But this would require 2 more conditions, to set the register D to,
// meaning that not keeping on DRY is better.


// Set the top-leftmost address to register 1
// In this program, R1 is used as a pixel counter

@RESTARTCOUNTER
0;JMP

(DRAWWHITE)
  // Set the pixel in R1 to white (0)
  @R1
  A=M
  M=0
  
  @LOOP
  0;JMP

(DRAWBLACK)
  // Set the pixel in R1 to black (1)
  D=0
  @R1
  A=M
  M=!D

  @LOOP
  0;JMP
  
(RESTARTCOUNTER)
  // Restart R1 when the screen was fully used
  @SCREEN
  D=A
  @R1
  M=D-1

(LOOP)
  // Check if screen is fully used
  @KBD
  D=A
  @R1
  D=D-M
  @RESTARTCOUNTER
  D;JEQ

  // Increment R1
  @R1
  M=M+1

  // Check for pressed key
  @KBD
  D=M

  @DRAWBLACK
  D;JNE

  @DRAWWHITE
  D;JEQ

  @LOOP
  0;JMP
