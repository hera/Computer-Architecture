"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256    # RAM storage
        self.pc = 0             # program counter
        self.ir = 0             # instruction register
        self.reg = [0] * 8
        self.working = False    # cpu is turned off by default

        self.instruction_table = {
            0b10000010: self.LDI,
            0b00000001: self.HLT,
            0b01000111: self.PRN
        }
    
    # Set the value of a register to an integer
    def LDI(self):
        self.pc += 1
        location = self.ram_read(self.pc)

        self.pc += 1
        data = self.ram_read(self.pc)

        self.reg[location] = data

    # Halt the CPU
    def HLT(self):
        self.working = False


    # Print numeric value stored in the given register
    def PRN(self):
        self.pc += 1

        location = self.ram_read(self.pc)
        data = self.reg[location]

        print(data)


    def ram_read(self, address):
        return self.ram[address]
    

    def ram_write(self, address, data):
        self.ram[address] = data


    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()


    def run(self):
        """Run the CPU."""
        
        self.working = True

        while self.working:
            # save a copy of the currently executing instruction into the instruction register (IR)
            self.ir = self.ram_read(self.pc)

            # check if the cpu supports this operation
            if self.ir in self.instruction_table:
                # call the handler
                self.instruction_table[self.ir]()

                self.pc += 1
            else:
                raise Exception(f"Unsupported operation: {self.ir}")