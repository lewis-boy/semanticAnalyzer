def main():
    types = ['int', 'float', 'bool']
    symbol_table  = {}

    def skip_whitespace(file):
        char = file.read(1)
        while char in [' ', '\t', '\n']:
            char = file.read(1)
        return char

    def read_word(file, first_char):
        word = [first_char]
        char = file.read(1)
        #read newline
        while char.isalnum() or char == '_' or char == '(' or char == ')':
            word.append(char)
            char = file.read(1)
        return ''.join(word), char

    #reads the RHS regardless if its a number or an expression like x + 1 + y
    def read_value(file, first_char):
        value = [first_char]
        char = file.read(1)
        while char and char not in [';', '\n']:
            value.append(char)
            char = file.read(1)
        return ''.join(value).strip()

    def is_valid_value(var_type, value):
        if var_type == 'int':
            return value.lstrip('-').isdigit()
        elif var_type == 'float':
            parts = value.lstrip('-').split('.')
            return len(parts) == 2 and all(part.isdigit() for part in parts)
        elif var_type == 'bool':
            return value in ['true', 'false']
        return False

    with open('case.txt', 'r') as source_code:
        for line in source_code:
            #line contains \n as well
            print(line, end= "$")

    return 0
    #     #line = file.readline()
    #     word = read_word(file, skip_whitespace(file))
    #     while word != '\n':
    #         # Skip whitespace to find the start of a line
    #         char = skip_whitespace(file)

    #         if not char:
    #             break

    #         # Check if line starts with a type (keyword)
    #         if char.isalpha():
    #             word, next_char = read_word(file, char)

    #             if word in types:
    #                 var_type = word
            
    #                 # Skip whitespace after type
    #                 while next_char in [' ', '\t']:
    #                     next_char = file.read(1)

    #                 # Read variable name
    #                 if not (next_char.isalpha() or next_char == '_'):
    #                     print("Invalid variable name start.")
    #                     continue
    #                 var_name, next_char = read_word(file, next_char)
    #                 if(var_name[-2:].strip() == "()"):
    #                     print(f"'{var_name}' is a function")
    #                 #Assignment
    #                 else:
    #                       # Skip whitespace before =
    #                     while next_char in [' ', '\t']:
    #                         next_char = file.read(1)

    #                     if next_char != '=':
    #                         print(f"Expected '=' after variable name '{var_name}'")
    #                         continue
    #                     # Skip whitespace after =
    #                     next_char = skip_whitespace(file)

    #                     # Read value
    #                     value = read_value(file, next_char)
    #                     # Validate
    #                     if is_valid_value(var_type, value):
    #                         symbol_table[var_name] = var_type
    #                         print(f"Valid: {var_type} {var_name} = {value}")
    #                     else:
    #                         print(f"Invalid assignment: {var_type} {var_name} = {value}")
                    
    #             else:
    #                 # Not a type declaration — skip rest of line (usage, etc.)
    #                 file.readline()
    #                 continue
    #         else:
    #             # Skip non-type lines
    #             file.readline()

    # print("\nCollected Variables:")
    # for var in symbol_table:
    #     print(var)


if __name__ == "__main__":
    main()