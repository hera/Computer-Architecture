"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256        # RAM storage
        self.pc = 0                 # program counter
        self.ir = 0                 # instruction register
        self.reg = [0] * 8
        self.working = False        # cpu is turned off by default
        self.sp = 7                 # the location in the IR that has a link to where the stack begins

        self.reg[self.sp] = 0xF4    # set the location in ram where the stack begins

        self.instruction_table = {
            0b10000010: self.LDI,
            0b00000001: self.HLT,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b10100000: self.ADD,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET
        }
        
    def CALL(self):
        self.pc += 1

        # save the next operation in stack
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + 1

        # go to the subroutine
        self.pc = self.reg[self.ram_read(self.pc)]

    
    def RET(self):
        
        next_address = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

        self.pc = next_address


    def PUSH(self):
        self.reg[self.sp] -= 1 # decrement the stack pointer

        address = self.ram_read(self.pc + 1) # from which instruction register I must take the value from
        data = self.reg[address] # get the value from the register

        # push the value on the stack
        self.ram[self.reg[self.sp]] = data

    def POP(self):
        copy_to = self.ram_read(self.pc + 1)

        value = self.ram_read(self.reg[self.sp])
        self.reg[copy_to] = value

        self.reg[self.sp] += 1
 
    # Set the value of a register to an integer
    def LDI(self):
        location = self.ram_read(self.pc + 1)

        data = self.ram_read(self.pc + 2)

        self.reg[location] = data

    # Halt the CPU
    def HLT(self):
        self.working = False


    # Print numeric value stored in the given register
    def PRN(self):
        location = self.ram_read(self.pc + 1)
        data = self.reg[location]

        print(data)


    # Multiply the values in registers A and B and store the result in registerA.
    def MUL(self):
        location_a = self.ram_read(self.pc + 1)
        location_b = self.ram_read(self.pc + 2)

        self.alu("MUL", location_a, location_b)
    
    # Add the values in two registers and store the result in the first one
    def ADD(self):
        location_a = self.ram_read(self.pc + 1)
        location_b = self.ram_read(self.pc + 2)

        self.alu("ADD", location_a, location_b)

    def ram_read(self, address):
        return self.ram[address]
    

    def ram_write(self, address, data):
        self.ram[address] = data


    def reg_read(self, address):
        return self.reg[address]


    def reg_write(self, address, data):
        self.reg[address] = data


    def load(self):
        """Load a program into memory."""

        # check if there's a file name
        if len(sys.argv) < 2:
            print("Error. Please provide a file name as a parameter")
            quit()

        path = sys.argv[1]
        raw_program = []

        # read the file an save as a list of lines
        try:
            file = open(path)
            raw_program = file.read().split("\n")
            file.close()
        except FileNotFoundError:
            print("Error. File not found.")
            quit()
        
        program = []

        for line in raw_program:
            operation = line.split("#")[0]
            operation = operation.strip()
            if len(operation):
                program.append(int(operation, 2))

        # check if the program can fit into ram
        if len(program) > len(self.ram):
            print("The program is too large. Please upgrade the RAM.")

        # load the program into ram
        for i in range(len(program)):
            self.ram[i] = program[i]


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
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

                sets_pc = self.ir >> 4 & 1 # get the 4th bit

                if not sets_pc:
                    num_operands = self.ir >> 6 # how many operands
                    self.pc += num_operands + 1 # move the pointer to the address after operands
            else:
                raise Exception(f"Unsupported operation: {self.ir:08b}")