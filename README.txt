----------------------------------------
how to use
----------------------------------------
1. instantiate the ram:
    ram = Ram(size_in_bits)
    example: ram = Ram(512)

2. allocate variables:
    - you can create int variables:
        ram.new_variable_left("a", 8, initial_value=0)
        this allocates an 8-bit variable named "a" and sets its initial value to 0.

    - you can create string variables:
        ram.new_variable_string_left("msg", "hello")
        this allocates memory for the string and stores "hello".

    - you can also allocate with alignment:
        ram.new_variable("varname", size_in_bits, initial_value, var_type="int", alignment=8)
        this tries to allocate memory at addresses divisible by 8.

3. getting and setting variables:
    - for int:
        val = ram["a"]  # reads the variable a
        ram["a"] = 10    # sets variable a to 10

    - for strings:
        s = ram.get_variable_string("msg")
        ram.set_variable_string("msg", "new stuff")

    - you can also increment and decrement int variables using:
        ram["a"] += 1
        ram["a"] -= 1

4. memory operations:
    - ram.allocate(size): allocates a random free block of given size
    - ram.allocate_left(size): allocates from the left side
    - ram.free(position, length): frees a block of memory
    - ram.write(position, data): writes binary data to a position
    - ram.read(position, length): reads binary data from a position
    - ram.read_int(position, length): reads an int from a position

    all these operations respect permissions. if you try to write where write is not allowed, you get an exception.

5. string and int conversions:
    - convert_dec_to_bin(dec, size): convert int to binary array
    - convert_bin_to_dec(bin_array): convert binary array to int
    - convert_string_to_bin(string): convert string to binary array
    - convert_bin_to_string(bin_array): convert binary array to string

6. permissions:
    - ram.set_permissions(position, length, read=True, write=True)
        sets read/write permissions for a memory range.

7. randomization:
    - ram.randomize(): randomizes used memory
    - ram.randomize_unused(): randomizes unused memory
    - ram.randomize_all(): randomizes all memory

8. correction and clones:
    the memory has three copies: main, clone_a, clone_b.
    - ram.correct(): uses majority vote to correct memory differences
    - ram.compare_memory(): shows differences between main and clones

9. rotation and reversal:
    - ram.rotate_left(how_many)
    - ram.rotate_right(how_many)
    - ram.reverse(position)
    - ram.reverse_all()

10. memory usage and dumping:
    - ram.memory_usage() returns the percentage of memory used.
    - ram.dump_memory() returns a list of binary strings (8 bits each).
    - ram.hex_dump() returns a hex representation of memory.

11. defragmentation:
    - ram.defragment(): tries to push used memory blocks to the left to reduce fragmentation.

12. scanning patterns:
    - ram.scan_for_pattern(pattern): finds all occurrences of a given bit pattern in memory.

13. paging:
    - ram.set_page_size(new_size)
    - ram.page_number(address): returns the page number for an address
    - ram.mark_page_used(page)
    - ram.mark_page_free(page)

14. saving/loading state:
    - ram.save("filename.pkl")
    - ram.load("filename.pkl")

----------------------------------------
made by trxixn/ravegoth
----------------------------------------
