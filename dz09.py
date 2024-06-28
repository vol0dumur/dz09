# ДЗ 09 - консольний бот-помічник

from re import sub


def add_phone_record(user_data=None) -> list:
    write_to_file("a", user_data[1:])

    return user_data[1:]


def change_phone_record(user_data=None) -> list:

    user_data[2] = reset_phone_format(user_data[2])
    phones[user_data[3]] = user_data[2]

    write_to_file("w", phones)

    return user_data[1:]


def delete_phone_record(user_data=None) -> list:

    global phones

    record_number = int(user_data[1])

    if record_number < 0 or record_number > len(phones) - 1:
        return False
    
    else:

        dict_key = list(phones.keys())[record_number]
        deleted_record = (dict_key, phones[dict_key])
        phones.pop(dict_key)
        write_to_file("w", phones)

        return list(deleted_record)


# Загальна функція для пошуку записів по імені або номеру.
# Використовується для роботи функцій з пошуку або редагування запису
def find_records(user_data, true_false_result=False) -> list | bool:

    matches_list = []
    is_phone = False

    if len(user_data) == 2:
        user_data[1] = reset_phone_format(user_data[1])
    else:

        # Якщо переданий у функцію параметр є номером телефону...
        if len(reset_phone_format(user_data[0])) == 12:

            user_data[0] = reset_phone_format(user_data[0])
            # ...то далі нам треба буде шукати в довіднику серед номерів
            is_phone = True

    j = user_data[0]

    for key, value in phones.items():
        if is_phone:
            # шукаємо серед номерів
            i = value 
        else:
            # шукаємо серед імен
            i = key
        if str(i).lower() == str(j).lower():
            matches_list.append(key)

    if len(matches_list) == 0:
        return False
    else:
        return true_false_result or matches_list


def find_phone_record(user_data=None) -> list:

    result = find_records(user_data[1:])

    if result == False:
        
        print("No records found.")

    else:

        print(f"Records found:")
        for num, item in enumerate(result):
            print(f"{str(num) + '.':<3} {item:<10} {restore_phone_format(phones[item])}")
    
    return result


def get_command_handler(command):
    return commands[command][0]


def greetings(message) -> str:
    result = input(f"{message}> ")

    return result


# Декоратор який обробляє усі помилки вводу користувача
def input_error(func) -> list:

    def inner(user_input):

        result = func(user_input)
        command_result = None
        number_of_user_parameters = len(result)

        if number_of_user_parameters == 0:

            # print("Empty input! Check your data.")
            return (False, None, 0)
        
        else:
            
            result[0] = result[0].lower()
            command = result[0]

            if command not in commands:
                return (False, command, 1)
                # print(f"'{command}' is not recognized as an internal command.\nType 'help' for help.")

            else:

                # Очікувану кількість параметрів беремо зі словника
                number_of_expected_parameters = commands[command][1]

                if len(result) < number_of_expected_parameters:
                    return (False, command, 2)
                    # print(f"Received command '{command}'. Too few parameters. Check your data.")

                elif len(result) > number_of_expected_parameters:
                    return (False, command, 3)
                    # print(f"Received command '{command}'. Too many parameters. Check your data.")

                else:

                    # Якщо очікувана кількість параметрів = 3, то треба перевірити введений користувачем номер телефону
                    if number_of_expected_parameters == 3:

                        if len(reset_phone_format(result[2])) != 12:

                            return (False, result[2], 4)
                            # print(f"'{result[2]}' is an incorrect phone number. It must contain 12 digits.\nCheck your data and repeat.")
                            # return None

                        # Якщо кількість введених параметрів правильна...
                        else:

                            # ...і користувач хоче додати запис - перевіряємо, чи існує вже таке ім'я користувача -
                            if command == "add": 
                                if find_records((result[1],), True):
                                    # - якщо ім'я існує, то повертаємо парамери в основну функцію, яка повідомить користувачу про це
                                    return (command, False)
                            elif command == "change":
                                # ...і користувач хоче редагувати запис - шукаємо по імені що редагувати
                                what_to_edit = find_records(result[1:])
                                if what_to_edit == False:
                                    # Якщо не знаходимо запис для редагування - повертаємо парамери в основну функцію, яка повідомить користувачу
                                    return (command, False)
                                else:
                                    # Інакше додаємо параметри в список параметрів
                                    result.append(what_to_edit[0])

                    command_handler = get_command_handler(command)
                    command_result = command_handler(result)

                    # Додатково обробляємо результат виконання команди, щоб головна функція
                    # повідомила користувачу про наявність проблем
                    if command_result:
                        command_result.insert(0, command)
                    else:
                        command_result = [command, False, result[1] if len(result) == 2 else None]

        return command_result
    
    return inner


def quit_bot(user_data=None) -> None:

    print("\nGood bye!\n")
    quit()


@input_error
def parse_user_input(user_input) -> list:

    if user_input:
        user_input = user_input.split()

    return user_input


def read_from_file() -> dict:
    
    result = {}

    try:

        with open(path_to_dic, "r") as f:
            file_data = f.readlines()

    except FileNotFoundError:

        with open(path_to_dic, "w") as f:
            f.write("")
        print(f"File '{path_to_dic}' was created.\nAdd at least 1 record before continue using bot.\nType 'help' for help.")

        return result

    for item in file_data:

        item_list = item.strip().split()
        result.update({item_list[0]: item_list[1]})
    
    print(f"{len(result)} phone records were loaded from file '{path_to_dic}'.")

    return result


def reset_phone_format(phone) -> str:
    return sub(r"[^0-9]", "", phone)


def restore_phone_format(phone) -> str:
    return f"+{phone[:3]}({phone[3:5]}){phone[5:8]}-{phone[8:10]}-{phone[10:]}"


def show_all_phone_records(user_data=None) -> None:

    if phones:
        for num, item in enumerate(phones):
            print(f"{str(num) + '.':<3} {item:<10} {restore_phone_format(phones[item])}")
    else:
        print("Phone list is empty.")


def say_hello(user_data=None) -> None:

    user_input = greetings("How can I help you? ")
    parse_user_input(user_input)


def show_help(user_data=None) -> None:
    
    print("""
    = = = = = = = = = = [ Help ] = = = = = = = = = =
    
    - display welcome message:
      hello
    - add a new record:
      add [name] [+380(00)000-00-00]
    - edit an existing record:
      change [name] [+380(00)000-00-00]
    - search a record by name or phone:
      phone [name] or [+380(00)000-00-00]
    - delete record with number from 'showall' list:
      delete [number]
    - show all records:
      showall
    - exit bot:
      goodbye/close/exit/quit/.
    
    = = = = = = = = = = = = = = = = = = = = = = = = =
    """)


def write_to_file(mode, data_to_write) -> bool:

    with open(path_to_dic, mode) as f:
        if mode == "a":
            f.write(f"{data_to_write[0]} {data_to_write[1]}\n")
        elif mode == "w":
            for i in data_to_write:
                f.write(f"{i} {data_to_write[i]}\n")
        else:
            return False
    
    return True


def main() -> None:
    
    global path_to_dic
    global phones

    msg = "Hello "
    path_to_dic = "phones.txt"
    phones = read_from_file()

    errors = (
        "Empty input! Check your data.",
        f"'user_data_1' is not recognized as an internal command.\nType 'help' for help.",
        f"Received command 'user_data_1'. Too few parameters. Check your data.",
        f"Received command 'user_data_1'. Too many parameters. Check your data.",
        f"'user_data_1' is an incorrect phone number. It must contain 12 digits.\nCheck your data and repeat."
    )

    # Вічний цикл очікування на команду користувача
    while True:

        user_input = greetings(msg)
        msg = ""

        user_data = parse_user_input(user_input)

        if len(phones) == 0:
            print("Add at least 1 record before continue using bot.")

        if user_data[0] == False:
            print(errors[user_data[2]].replace("user_data_1", user_data[1]))

        if user_data:

            match user_data[0]:

                case "add":

                    if user_data[1] == True:
                        print(f"Record with name '{user_data[1]}' already exists!\nCheck your data and repeat.")
                    else:
                        phones.update({user_data[1]: reset_phone_format(user_data[2])})
                        print(f"Record ({user_data[1]}, {restore_phone_format(user_data[2])}) was successfully added.")

                case "change":

                    if user_data[1] == False:
                        print("Couldn't find any matches for your query.\nCheck your data and repeat.")
                    else:
                        print(f"Record ({user_data[1]}, {restore_phone_format(user_data[2])}) was successfully changed.")

                case "delete":

                    if user_data[1] == False:
                        print(f"Cannot delete record #{user_data[2]}. This number is out of range.")
                    else:
                        print(f"Record ({user_data[1]}, {restore_phone_format(user_data[2])}) was successfully deleted.")


# Цифра після назви функції - кількість параметрів, яку приймає ця функція
commands = {
    "add": (add_phone_record, 3),
    "phone": (find_phone_record, 2),
    "change": (change_phone_record, 3),
    "delete": (delete_phone_record, 2),
    "showall": (show_all_phone_records, 1),
    "help": (show_help, 1),
    "hello": (say_hello, 1),
    "hi": (say_hello, 1),
    "goodbye": (quit_bot, 1),
    "close": (quit_bot, 1),
    "exit": (quit_bot, 1),
    "quit": (quit_bot, 1),
    ".": (quit_bot, 1)
}

if __name__ == "__main__":
    main()