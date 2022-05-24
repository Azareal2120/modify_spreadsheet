import csv


def read_command(name, command, spreadsheet):
    """Takes in the input from the user, and decides what to do"""

    # Splits the command into separate words
    command = command.split(" ")
    if command[0] == "h" and len(command) == 1:
        print("    These are the available commands:")
        print("        h: Prints all available commands,")
        print(
            f"        a <{field_names[0]}> <{field_names[1]}> [{field_names[2]}] <{field_names[3]}> <{field_names[4]}> <{field_names[5]}>: Adds an item to the list,"
        )
        print("        p: Prints the full sheet")
        print("        f: Prints all components requiring reorder")
        print(f"        r <{field_names[0]}> <{field_names[1]}> [{field_names[2]}] <quantity>: Removes the given quantity from the sheet")
        print("        readfile <filename>: Reads a text file and processes each command line by line")
        print("        s <type> <subtype> [special]: Searches for any elements that fit the given parameters")
    elif command[0] == "a":
        add_row(name, command, spreadsheet)
    elif command[0] == "p" and len(command[0]) == 1:
        print_sheet(name, spreadsheet)
    elif command[0] == "f" and len(command[0]) == 1:
        find_reorder(name)
    elif command[0] == "r":
        remove_element(name, command)
    elif command[0] == "readfile":
        open_file(name, command, spreadsheet)
    else:
        print("invalid command")


def add_row(name, command, spreadsheet):
    if len(command) == 7:
        # Adding a full row
        new_dict = {
            "type": command[1],
            "subtype": command[2],
            "special": command[3],
            "value": command[4],
            "quantity": command[5],
            "num_reorder": command[6].rstrip(),
            "to_reorder": command[5] > command[6],
        }

        print(f"Adding: {new_dict}")
        is_dupe = check_duplicates(name, command, spreadsheet, "full")
        if not is_dupe:
            print("Adding full row")
            spreadsheet.writerow(new_dict) 
        else:
            print("Duplicate found, adding quantity")
    elif len(command) == 6:
        # Adding a partial row
        new_dict = {
            "type": command[1],
            "subtype": command[2],
            "special": "",
            "value": command[3],
            "quantity": command[4],
            "num_reorder": command[5].rstrip(),
            "to_reorder": command[4] > command[5],
        }
        print(f"Adding: {new_dict}")
        is_dupe = check_duplicates(name, command, spreadsheet, "partial")
        if not is_dupe:
            print("Adding partial row")
            spreadsheet.writerow(new_dict)  
        else:
            print("Duplicate found, adding quantity")
    else:
        # Invalid row
        print("Invalid addition command")


def check_duplicates(name, command, spreadsheet, operation):
    # Opening the file as a reader
    with open(name, mode="r", newline="", encoding="utf-8-sig") as read_file:
        r = csv.reader(read_file)
        r = list(r)
        if operation == "full":
            check_list = [0,1,2,3]
        elif operation == "partial":
            check_list = [0,1,3]
        for rows in r:
            # Checking for duplicity
            is_dupe = do_check_duplicates(name, command, rows, operation, check_list)
            # If there is a dupe, adds the quantities together
            if is_dupe:
                if operation == "full":
                    rows[4] = int(rows[4]) + int(command[5])
                if operation == "partial":
                    rows[4] = int(rows[4]) + int(command[4])
                overwrite_file(name, r)
                return True
    return False
            

def overwrite_file(name, spreadsheet):
    # Rewrites the orginal csv file using the new reader
    with open(name, mode="w", newline="") as write_file:
        writer = csv.writer(write_file)
        for rows in spreadsheet:
            writer.writerow(rows)
    

def do_check_duplicates(name, command, row, operation, check_list):
    if operation == "full":
        return do_check_duplicates_full(command, row, check_list)
    elif operation == "partial":
        return do_check_duplicates_partial(command, row, check_list)
    else:
        return False


def do_check_duplicates_full(command, row, check_list):
    for elements in check_list:
        if command[elements + 1] != row[elements]:
            return False
    return True


def do_check_duplicates_partial(command, row, check_list):
    for index, elements in enumerate(check_list):
        if index < 2:
            if command[elements + 1] != row[elements]:
                return False
        elif command[elements] != row[elements]:
            return False
    if row[2] == "":
        return True
    else:
        return False


def find_reorder(name):
    # Creates a list version of the spreadsheet
    with open(name, mode="r", newline="") as read_file:
        r = csv.reader(read_file)
        r = list(r)
        # Creates an empty list to add reorders to
        reorder_list = []
        for rows in r:
            if rows[6].lower() == "true":
                reorder_list.append(rows)
        print("The following components are ready for reorder:")
        for components in reorder_list:
            print(components)


def remove_element(name, command):
    # Loops through the list to find the required elements
    with open(name, mode="r", newline="") as read_file:
        r = csv.reader(read_file)
        r = list(r)
        for rows in r:
            if len(command) == 5:
                check_list = [0,1,3]   
                operation = "partial"    
            elif len(command) == 6:
                check_list = [0,1,2,3]
                operation = "full"
            else:
                print("Invalid Length")
                return
            if do_check_duplicates(name, command, rows, operation, check_list):
                print("found a duplicate")
                if operation == "partial" and rows[2] != "":
                    print("Item not found")
                    return
                elif operation == "full":
                    rows[4] = int(rows[4]) - int(command[5])
                    print("Full removal")
                elif operation == "partial":
                    print("Partial removal")
                    rows[4] = int(rows[4]) - int(command[4])
                if rows[4] < 0:
                    rows[4] = 0
                print("Removed quantity")
    overwrite_file(name, r)


def print_sheet(name, spreadsheet):
    with open(name, mode="r", newline="", encoding="utf-8-sig") as csv_file:
        full_sheet = csv.reader(csv_file)
        for row in full_sheet:
            print(row)


def open_file(name, command, spreadsheet):
    filename = command[1]
    with open(filename) as file:
        for line in file:
            with open(name, mode="a", newline="", encoding="utf-8-sig") as csv_file:
                spreadsheet = csv.DictWriter(csv_file, fieldnames=field_names)
                read_command(name,line,spreadsheet)


if __name__ == "__main__":
    # Loads the spreadsheet given a name
    name = input("What csv file do you wish to edit? ")
    print(f"Editing {name}")
    with open(name, mode="r", newline="", encoding="utf-8-sig") as csv_file:
        init_sheet = csv.reader(csv_file)
        global field_names
        field_names = []
        num_lines = 0
        for row in init_sheet:
            if num_lines == 0:
                for names in row:
                    field_names.append(names.lower())
            num_lines += 1
    while 1:
        # Takes in a command
        command = input("Please enter a command, type 'h' for help: ")
        if command == "q":
            break
        else:
            with open(name, mode="a", newline="", encoding="utf-8-sig") as csv_file:
                spreadsheet = csv.DictWriter(csv_file, fieldnames=field_names)
                read_command(name, command, spreadsheet)
