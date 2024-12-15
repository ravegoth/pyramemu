from ramemu import Ram

# initialize ram with 512 bits
ram = Ram(512)

# create int variables aligned to the left
ram.new_variable_left("a", 8, 0)
ram.new_variable_left("b", 8, 0)
ram.new_variable_left("result", 8, 0)

# create string variables aligned to the left
ram.new_variable_string_left("prompt_a", "enter a: ")
ram.new_variable_string_left("prompt_b", "enter b: ")
ram.new_variable_string_left("echo_result", "the result is:")

# get user input to set variables a and b
ram.set_variable("a", int(input(ram.get_variable_string("prompt_a"))))
ram.set_variable("b", int(input(ram.get_variable_string("prompt_b"))))

# compute result = a + b
ram.set_variable("result", ram.get_variable("a") + ram.get_variable("b"))

# print the result
print(ram.get_variable_string("echo_result"), ram.get_variable("result"))

# create more variables to test increments and decrements
ram.new_variable_left("c", 8, 10)
ram["c"] += 1
ram["c"] -= 1
print("c:", ram["c"])  # should be back to 10

# test string variable creation and updating
ram.new_variable_string_left("greet", "hello")
print("greet before:", ram.get_variable_string("greet"))
ram.set_variable_string("greet", "hey")
print("greet after:", ram.get_variable_string("greet"))

# test permissions
pos, size = ram.variables["greet"]
ram.set_permissions(pos, size, read=True, write=False)  # greet is now read-only
try:
    ram.set_variable_string("greet", "nope")  # should fail
except Exception as e:
    print("write permission test passed, got exception:", e)

# test aligned allocation
ram.new_variable("aligned_int", 16, 1234, var_type="int", alignment=8)
print("aligned_int:", ram["aligned_int"])

# test free and defragment
ram.new_variable_left("x", 8, 42)
ram.new_variable_left("y", 8, 100)
ram.free(ram.variables["x"][0], ram.variables["x"][1])  # free x
print("memory usage before defragment:", ram.memory_usage(), "%")
ram.defragment()
print("memory usage after defragment:", ram.memory_usage(), "%")

# test dumping memory and hex dump
print("memory dump (binary):", ram.dump_memory())
print("memory dump (hex):", ram.hex_dump())

# test saving and loading state
ram.save("ram_state.pkl")
ram_loaded = Ram(512)
ram_loaded.load("ram_state.pkl")
print("loaded ram greet variable:", ram_loaded.get_variable_string("greet"))

# test randomize functions
ram.randomize_unused()
print("randomized unused memory (hex):", ram.hex_dump())
ram.randomize_all()
print("randomized all memory (hex):", ram.hex_dump())

# test correct function after corrupting clones
if ram.size > 10:
    ram.memory_clone_a[10] = 1 - ram.memory_clone_a[10]
    ram.memory_clone_b[11] = 1 - ram.memory_clone_b[11]
diffs = ram.compare_memory()
print("differences before correction:", diffs)
ram.correct()
print("differences after correction:", ram.compare_memory())

# test scanning for a pattern
pattern = [0,1,0,1]
matches = ram.scan_for_pattern(pattern)
print("pattern", pattern, "found at:", matches)

# test paging
ram.set_page_size(64)
print("page number for address 10:", ram.page_number(10))
ram.mark_page_used(ram.page_number(10))
print("pages:", ram.pages)

print("done testing")
