# ДЗ 09 - консольний бот-помічник

from re import sub


class PhoneListIsEmpty(Exception):
    def __init__(self, message=None):
        self.message = message


class RecordAlreadyExists(Exception):
    def __init__(self, message=None):
        self.message = message


class TooLessParameters(Exception):
    def __init__(self, message=None):
        self.message = message


class TooMuchParameters(Exception):
    def __init__(self, message=None):
        self.message = message


class WrongPhone(Exception):
    def __init__(self, message=None):
        self.message = message


class WrongRecordNumber(Exception):
    def __init__(self, message=None):
        self.message = message


def check_params(user_data) -> bool:
    
    number_of_expected_parameters = commands[user_data[0]][1]

    if len(user_data) > number_of_expected_parameters:
        raise TooMuchParameters
    elif len(user_data) <= number_of_expected_parameters - 1:
        raise TooLessParameters
    
    if len(user_data) == 3:
        if len(reset_phone_format(user_data[2])) != 12:
            raise WrongPhone
        
    if user_data[0] == "add": 
        if find_records((user_data[1],), True):
            # Якщо ім'я існує, то повертаємо виключення в основну функцію, яка повідомить користувачу про помилку введення
            raise RecordAlreadyExists

    return True


def add_phone_record(user_data=None) -> list:

    if not check_params(user_data):
        return (False, user_data[0], user_data[1])
    
    write_to_file("a", user_data[1:])

    return user_data[1:]


def change_phone_record(user_data=None) -> list:

    if len(phones) == 0:
        raise PhoneListIsEmpty

    if not check_params(user_data):
        return (False, user_data[1], user_data[2])

    user_data[2] = reset_phone_format(user_data[2])
    phones[user_data[1].capitalize()] = user_data[2]

    write_to_file("w", phones)

    return (user_data[1].capitalize(), user_data[2])


def delete_phone_record(user_data=None) -> list:

    global phones

    record_number = int(user_data[1])

    if record_number in tuple(range(len(phones))):
        
        dict_key = list(phones.keys())[record_number]
        phone_number = phones[dict_key]
        phones.pop(dict_key)

        write_to_file("w", phones)
        
        return (dict_key, phone_number)
    
    else:
        raise WrongRecordNumber


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

    if not check_params(user_data):
        return (False, user_data[0], user_data[1])
    
    result = find_records(user_data[1:])

    if result == False:
        
        print("No records found.")
        return (None,)

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
        command_result = [False, ""]
        command = None
        
        try:

            result[0] = result[0].lower()
            command = result[0]
            command_handler = get_command_handler(command)
            command_result = command_handler(result)
        
        except Exception as error:
            return (False, type(error).__name__, command, result[1] if len(result) >= 2 else None, result[2] if len(result) == 3 else None)
        
        else:
            return (True, command, *command_result)
        
        finally:

            if command_result == False:
                print(f"command {command} returned bad result")
                command_result = (False, False)
            elif command_result == None:
                print(f"command {command} returned bad result")
                command_result = (True, None)

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


def show_all_phone_records(user_data=None) -> int:

    if phones:
        for num, item in enumerate(phones):
            print(f"{str(num) + '.':<3} {item:<10} {restore_phone_format(phones[item])}")
    else:
        print("Phone list is empty.")

    return (len(phones),)


def say_hello(user_data=None) -> str:
    return ("How can I help you? ",)


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

    return (None,)


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
        "Empty input!user_data", 
        f"'user_data' is not recognized as an internal command.",
        f"Received command 'user_data'. Too few parameters.",
        f"Received command 'user_data'. Too many parameters.",
        f"'user_data' is an incorrect phone number. It must contain 12 digits.",
        f"Name 'user_data' already exists!",
        f"Cannot delete record. Number 'user_data' is out of range.",
        "Phone list is empty!user_data"
    )

    # Вічний цикл очікування на команду користувача
    while True:

        user_input = greetings(msg)
        msg = ""

        user_data = parse_user_input(user_input)

        if len(phones) == 0:
            print("Add at least 1 record before continue using bot.")

        # Обробляємо неуспішне виконання функції
        if user_data[0] == False:

            match user_data[1]:

                case "IndexError":
                    print(errors[0].replace("user_data", ""))

                case "KeyError":
                    print(errors[1].replace("user_data", user_data[2]))

                case "TooLessParameters":
                    print(errors[2].replace("user_data", user_data[2]))

                case "TooMuchParameters":
                    print(errors[3].replace("user_data", user_data[2]))

                case "WrongPhone":
                    print(errors[4].replace("user_data", user_data[4]))

                case "RecordAlreadyExists":
                    print(errors[5].replace("user_data", user_data[3]))

                case "WrongRecordNumber":
                    print(errors[6].replace("user_data", user_data[3]))

                case "PhoneListIsEmpty":
                    print(errors[7].replace("user_data", ""))

                case False:
                    print("Common error.")

            print("Check your data and repeat or type 'help' for help.")
        
        # Обробляємо успішне виконання функції
        elif user_data[0] == True:

            match user_data[1]:

                case "hello":
                    msg = user_data[2]

                case "delete":
                    print(f"Record ({user_data[2]}, {restore_phone_format(user_data[3])}) was successfully deleted.")

                case "add":
                    phones.update({user_data[2].capitalize(): reset_phone_format(user_data[3])})
                    print(f"Record ({user_data[2]}, {restore_phone_format(user_data[3])}) was successfully added.")

                case "showall":
                    print(f"\nA total of {user_data[2]} records were shown.")

                case "change":
                    print(f"Record ({user_data[2]}, {restore_phone_format(user_data[3])}) was successfully changed.")


# Цифра після назви функції - кількість параметрів, які приймає ця функція
commands = {
    "add": (add_phone_record, 3),
    "phone": (find_phone_record, 2),
    "change": (change_phone_record, 3),
    "delete": (delete_phone_record, 2),
    "showall": (show_all_phone_records, 1),
    "help": (show_help, 1),
    "hello": (say_hello, 1),
    "goodbye": (quit_bot, 1),
    "close": (quit_bot, 1),
    "exit": (quit_bot, 1),
    "quit": (quit_bot, 1),
    ".": (quit_bot, 1)
}

if __name__ == "__main__":
    main()