import random
import pickle

class Ram:
    def __init__(self, size):  # size in bits
        # this shit initializes the ram with given size and clones
        # also tracks usage and variable allocation
        self.size = size
        self.memory = [0] * size
        self.memory_clone_a = [0] * size
        self.memory_clone_b = [0] * size
        self.is_used = [False] * size
        self.variables = {}
        # permissions: store permissions as tuples (read, write) per bit
        self.permissions = [(True, True)] * size  
        # store variable metadata like type (int, string), alignment, etc.
        self.variable_metadata = {}
        # store pages info for paging simulation
        self.page_size = 64  # default page size, can be changed
        self.pages = [False] * (size // self.page_size)

    def set_permissions(self, position, length, read=True, write=True):
        # sets permissions for a range of memory bits
        # read/write are booleans
        for i in range(length):
            self.permissions[position + i] = (read, write)

    def check_permissions(self, position, length, for_write=False):
        # checks if a given range of memory is accessible for read or write
        for i in range(length):
            r, w = self.permissions[position + i]
            if for_write and not w:
                raise Exception("write permission denied at position {}".format(position + i))
            if not for_write and not r:
                raise Exception("read permission denied at position {}".format(position + i))

    def allocate(self, size):
        # allocate memory randomly, tries 100 times
        attempts = 0
        while attempts < 100:
            position = random.randint(0, self.size - size)
            if all(not self.is_used[position + i] for i in range(size)):
                for i in range(size):
                    self.is_used[position + i] = True
                return position
            attempts += 1
        raise Exception("not enough memory after 100 attempts.")

    def allocate_left(self, size):
        # allocate memory as left as possible (where free)
        for position in range(self.size - size + 1):
            if all(not self.is_used[position + i] for i in range(size)):
                for i in range(size):
                    self.is_used[position + i] = True
                return position
        raise Exception("not enough memory.")

    def write(self, position, data):
        # write data at position, also update clones and permissions
        length_of_data = len(data)
        self.check_permissions(position, length_of_data, for_write=True)
        for i in range(length_of_data):
            self.memory[position + i] = data[i]
            self.memory_clone_a[position + i] = data[i]
            self.memory_clone_b[position + i] = data[i]
            self.is_used[position + i] = True

    def convert_dec_to_bin(self, dec, size=None):
        # converts decimal to binary (two's complement if negative)
        if dec == 0 and size is not None:
            return [0] * size
        bin_array = []
        is_negative = dec < 0
        dec = abs(dec)
        while dec > 0:
            bin_array.append(dec % 2)
            dec //=2
        bin_array.reverse()
        if size:
            # pad binary number to match size
            bin_array = [0] * (size - len(bin_array)) + bin_array
        if is_negative:
            # use two's complement for negative numbers
            bin_array = self.twos_complement(bin_array, size)
        return bin_array

    def twos_complement(self, bin_array, size):
        # ensures two's complement
        bin_array = [0] * (size - len(bin_array)) + bin_array
        bin_array = [1 - bit for bit in bin_array]
        carry = 1
        for i in range(size - 1, -1, -1):
            if bin_array[i] == 0 and carry == 1:
                bin_array[i] = 1
                carry = 0
            elif bin_array[i] == 1 and carry == 1:
                bin_array[i] = 0
                carry = 1
        return bin_array

    def convert_bin_to_dec(self, bin_array):
        # converts binary array (two's complement) to decimal
        if len(bin_array) == 0:
            return 0
        is_negative = bin_array[0] == 1
        if is_negative:
            # two's complement negative
            bin_copy = self.twos_complement(bin_array[:], len(bin_array))
            value = -sum(bin_copy[i] * (2 ** (len(bin_copy) - i - 1)) for i in range(len(bin_copy)))
        else:
            value = sum(bin_array[i] * (2 ** (len(bin_array) - i - 1)) for i in range(len(bin_array)))
        return value

    def convert_string_to_bin(self, string):
        # converts string to binary array (8 bits per char)
        bin_array = []
        for char in string:
            bin_array.extend([int(bit) for bit in format(ord(char), '08b')])
        return bin_array

    def convert_bin_to_string(self, bin_array):
        # converts binary array to string (8 bits per char)
        chars = []
        for i in range(0, len(bin_array), 8):
            byte = bin_array[i:i+8]
            byte_val = int(''.join(map(str, byte)), 2)
            chars.append(chr(byte_val))
        return ''.join(chars)

    def read(self, position, length):
        # read data from memory
        self.check_permissions(position, length, for_write=False)
        data = []
        for i in range(length):
            data.append(self.memory[position + i])
        return data

    def read_int(self, position, length):
        # read an integer from memory
        data = self.read(position, length)
        return self.convert_bin_to_dec(data)

    def free(self, position, length):
        # free memory
        self.check_permissions(position, length, for_write=True)
        for i in range(length):
            self.memory[position + i] = 0
            self.memory_clone_a[position + i] = 0
            self.memory_clone_b[position + i] = 0
            self.is_used[position + i] = False
            self.permissions[position + i] = (True, True)

    def set(self, position, data):
        # set a single bit, with permissions check
        self.check_permissions(position, 1, for_write=True)
        self.memory[position] = data
        self.memory_clone_a[position] = data
        self.memory_clone_b[position] = data

    def get(self, position):
        # get a single bit
        self.check_permissions(position, 1, for_write=False)
        return self.memory[position]

    def reverse(self, position):
        # flip a single bit
        self.check_permissions(position, 1, for_write=True)
        self.memory[position] = 1 - self.memory[position]
        self.memory_clone_a[position] = 1 - self.memory_clone_a[position]
        self.memory_clone_b[position] = 1 - self.memory_clone_b[position]

    def reverse_all(self):
        # flip all used bits
        for i in range(self.size):
            if self.is_used[i]:
                self.check_permissions(i, 1, for_write=True)
                self.memory[i] = 1 - self.memory[i]
                self.memory_clone_a[i] = 1 - self.memory_clone_a[i]
                self.memory_clone_b[i] = 1 - self.memory_clone_b[i]

    def __str__(self):
        # returns a string of bits
        return "".join(map(str, self.memory))

    def rotate_right(self, how_many):
        # circular shift to the right
        how_many = how_many % self.size
        last_bits = self.memory[-how_many:]
        self.memory = last_bits + self.memory[:-how_many]
        self.memory_clone_a = last_bits + self.memory_clone_a[:-how_many]
        self.memory_clone_b = last_bits + self.memory_clone_b[:-how_many]

    def rotate_left(self, how_many):
        # circular shift to the left
        how_many = how_many % self.size
        first_bits = self.memory[:how_many]
        self.memory = self.memory[how_many:] + first_bits
        self.memory_clone_a = self.memory_clone_a[how_many:] + first_bits
        self.memory_clone_b = self.memory_clone_b[how_many:] + first_bits

    def to_string(self):
        # convert all the memory from binary to string (only makes sense if divisible by 8)
        return self.convert_bin_to_string(self.memory)

    def new_variable(self, name, size, initial_value=0, var_type="int", alignment=1):
        # create a new variable of given size (in bits)
        # if alignment > 1, try to align
        aligned_pos = self.allocate_aligned(size, alignment)
        self.variables[name] = (aligned_pos, size)
        bin_value = self.convert_dec_to_bin(initial_value, size)
        self.write(aligned_pos, bin_value)
        self.variable_metadata[name] = {
            "type": var_type,
            "alignment": alignment
        }

    def allocate_aligned(self, size, alignment):
        # allocate memory aligned to a certain boundary
        # tries to find a chunk starting at a multiple of alignment
        for pos in range(0, self.size - size + 1, alignment):
            if all(not self.is_used[pos + i] for i in range(size)):
                for i in range(size):
                    self.is_used[pos + i] = True
                return pos
        raise Exception("not enough aligned memory.")

    def new_variable_left(self, name, size, initial_value=0, var_type="int", alignment=1):
        # aligned, from the left side
        # basically the same as allocate_left but with alignment
        for pos in range(0, self.size - size + 1, alignment):
            if all(not self.is_used[pos + i] for i in range(size)):
                for i in range(size):
                    self.is_used[pos + i] = True
                self.variables[name] = (pos, size)
                bin_value = self.convert_dec_to_bin(initial_value, size)
                self.write(pos, bin_value)
                self.variable_metadata[name] = {
                    "type": var_type,
                    "alignment": alignment
                }
                return
        raise Exception("not enough memory.")

    def new_variable_string(self, name, string, alignment=1):
        # create a new string variable
        bin_value = self.convert_string_to_bin(string)
        pos = self.allocate_aligned(len(bin_value), alignment)
        self.variables[name] = (pos, len(bin_value))
        self.write(pos, bin_value)
        self.variable_metadata[name] = {
            "type": "string",
            "alignment": alignment
        }

    def new_variable_string_left(self, name, string, alignment=1):
        # create a new string variable aligned and from the left
        bin_value = self.convert_string_to_bin(string)
        for pos in range(0, self.size - len(bin_value) + 1, alignment):
            if all(not self.is_used[pos + i] for i in range(len(bin_value))):
                for i in range(len(bin_value)):
                    self.is_used[pos + i] = True
                self.variables[name] = (pos, len(bin_value))
                self.write(pos, bin_value)
                self.variable_metadata[name] = {
                    "type": "string",
                    "alignment": alignment
                }
                return
        raise Exception("not enough memory.")

    def get_variable(self, name):
        position, size = self.variables[name]
        bin_value = self.read(position, size)
        # if type is int
        if self.variable_metadata[name]["type"] == "int":
            return self.convert_bin_to_dec(bin_value)
        else:
            # if it's not int, assume something else
            return bin_value

    def get_variable_string(self, name):
        position, size = self.variables[name]
        bin_value = self.read(position, size)
        return self.convert_bin_to_string(bin_value)

    def __getitem__(self, name):
        # get value of variable by name
        return self.get_variable(name)

    def __setitem__(self, name, value):
        # set value of variable by name
        self.set_variable(name, value)

    def __iadd__(self, name):
        # increment variable by 1
        val = self.get_variable(name)
        self.set_variable(name, val + 1)
        return self

    def __isub__(self, name):
        # decrement variable by 1
        val = self.get_variable(name)
        self.set_variable(name, val - 1)
        return self

    def set_variable(self, name, value):
        # sets variable's value
        position, size = self.variables[name]
        if self.variable_metadata[name]["type"] == "int":
            bin_value = self.convert_dec_to_bin(value, size)
            self.write(position, bin_value)
        else:
            raise Exception("cannot set non-int variable this way.")

    def set_variable_string(self, name, string):
        # sets a string variable
        position, size = self.variables[name]
        bin_value = self.convert_string_to_bin(string)
        if len(bin_value) > size:
            raise Exception("new string is larger than allocated space.")
        # pad if smaller
        bin_value = bin_value + [0]*(size - len(bin_value))
        self.write(position, bin_value)

    def randomize(self):
        # randomize used memory
        for i in range(self.size):
            if self.is_used[i]:
                self.check_permissions(i, 1, for_write=True)
                val = random.randint(0,1)
                self.memory[i] = val
                self.memory_clone_a[i] = val
                self.memory_clone_b[i] = val

    def randomize_unused(self):
        # randomize unused memory
        for i in range(self.size):
            if not self.is_used[i]:
                val = random.randint(0,1)
                self.memory[i] = val
                self.memory_clone_a[i] = val
                self.memory_clone_b[i] = val

    def randomize_all(self):
        # randomize entire memory
        for i in range(self.size):
            val = random.randint(0,1)
            self.memory[i] = val
            self.memory_clone_a[i] = val
            self.memory_clone_b[i] = val

    def save(self, filename):
        # save all the properties of the ram object to a file
        # saving entire __dict__
        with open(filename, "bw") as file:
            pickle.dump(self.__dict__, file)

    def load(self, filename):
        # load all the properties of the ram object from a file
        with open(filename, "br") as file:
            self.__dict__.update(pickle.load(file))

    def correct(self):
        # correct the memory using the two clones
        for i in range(self.size):
            if self.memory_clone_a[i] == self.memory_clone_b[i]:
                self.memory[i] = self.memory_clone_a[i]
            else:
                values = [self.memory[i], self.memory_clone_a[i], self.memory_clone_b[i]]
                # majority vote
                self.memory[i] = max(set(values), key=values.count)

    def compare_memory(self):
        # compare the memory with the two clones and return the indexes of differences
        differences = []
        for i in range(self.size):
            if (self.memory[i] != self.memory_clone_a[i]) or (self.memory[i] != self.memory_clone_b[i]):
                differences.append(i)
        return differences

    def memory_usage(self):
        # percentage of memory used
        used_memory = sum(self.is_used)
        return (used_memory / self.size) * 100

    def dump_memory(self):
        # dump memory in 8-bit chunks
        return [''.join(map(str, self.memory[i:i+8])) for i in range(0, self.size, 8)]

    def hex_dump(self):
        # hex dump for a more realistic memory inspection
        output = []
        for i in range(0, self.size, 8):
            byte_str = self.memory[i:i+8]
            byte_val = int(''.join(map(str, byte_str)), 2)
            output.append('{:02X}'.format(byte_val))
        return ' '.join(output)

    def defragment(self):
        # simple defragmentation: push used blocks to the left
        new_memory = []
        new_usage = []
        # extract all used bits
        for i in range(self.size):
            if self.is_used[i]:
                new_memory.append(self.memory[i])
                new_usage.append(True)
        # fill the rest with zeros
        unused_len = self.size - len(new_memory)
        new_memory.extend([0]*unused_len)
        new_usage.extend([False]*unused_len)
        self.memory = new_memory
        self.memory_clone_a = new_memory[:]
        self.memory_clone_b = new_memory[:]
        self.is_used = new_usage
        # variables need to be relocated if we kept track of addresses
        # for simplicity, we lose variable info or try re-map them if we had a better map
        # this is a simplistic approach, so careful with defragmentation usage, 

    def where(self, name):
        # convert to hex
        return hex(self.variables[name][0])
    
    def size_of(self, name):
        return self.variables[name][1]

    def scan_for_pattern(self, pattern):
        # scan memory for a given bit pattern (list of bits)
        # returns all starting indexes where pattern is found
        matches = []
        plen = len(pattern)
        for i in range(self.size - plen + 1):
            if self.memory[i:i+plen] == pattern:
                matches.append(i)
        return matches

    def set_page_size(self, new_size):
        # set a new page size, re-initialize pages
        if self.size % new_size != 0:
            raise Exception("page size must evenly divide total memory size.")
        self.page_size = new_size
        self.pages = [False] * (self.size // self.page_size)

    def page_number(self, address):
        # get page number for a given address
        return address // self.page_size

    def mark_page_used(self, page_num):
        # mark a page as used
        if page_num < len(self.pages):
            self.pages[page_num] = True

    def mark_page_free(self, page_num):
        # mark a page as free
        if page_num < len(self.pages):
            self.pages[page_num] = False

if __name__ == "__main__":
    print("this is a library to be used in other programs")
