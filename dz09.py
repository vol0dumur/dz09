# ДЗ 09 - консольний бот-помічник

from re import sub


def input_error(func):

    def inner(user_data):
        
        try:

            check_params(user_data)
            command_result = func(user_data)

        except Exception as error:
            command_result = [False, str(error)]

        return command_result
    
    return inner


@input_error
def add_phone_record(user_data=None) -> list:

    if len(phones) != 0 and find_records((user_data[1],), True):
        # Якщо ім'я існує, то повертаємо виняток в основну функцію, 
        # яка повідомить користувачу про помилку введення
        raise TypeError("RecordAlreadyExists")

    if user_data[1].isnumeric():
        raise TypeError("WrongUserName")
    
    phones.update({user_data[1].capitalize(): reset_phone_format(user_data[2])})

    return [user_data[0], [user_data[1].capitalize(), user_data[2]]]


@input_error
def change_phone_record(user_data=None) -> list:

    if len(phones) == 0:
        raise TypeError("PhoneListIsEmpty")
    
    result_phone = reset_phone_format(user_data[2])
    result_name = user_data[1].capitalize()

    if find_records([result_name], True):
        phones[result_name] = result_phone
    else:
        raise TypeError("NoSuchRecord")

    return [user_data[0], [result_name, result_phone]]


# Перевіряємо загальні параметри перед запуском основних функцій.
# Щоб не виловлювати проблеми безпосередньо у функціях і не роздувати їх код.
def check_params(user_data) -> bool:

    if isinstance(user_data, str):
        return False
    
    else:
    
        number_of_expected_parameters = commands[user_data[0]][1]

        if len(user_data) > number_of_expected_parameters:
            raise TypeError("TooManyParameters")
        elif len(user_data) <= number_of_expected_parameters - 1:
            raise TypeError("TooFewParameters")
        
        if len(user_data) == 3 and len(reset_phone_format(user_data[2])) != 12:
            raise TypeError("WrongPhone")

        return True


@input_error
def delete_phone_record(user_data=None) -> list:

    global phones

    record_number = int(user_data[1])

    if record_number in tuple(range(len(phones))):
        
        dict_key = list(phones.keys())[record_number]
        phone_number = phones[dict_key]
        phones.pop(dict_key)
        
        return [user_data[0], [dict_key, phone_number], user_data[1]]
    
    else:
        raise TypeError("WrongRecordNumber")
    

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
            matches_list.append(f"{key:<10} {restore_phone_format(value)}")

    if len(matches_list) == 0:
        return False
    else:
        return true_false_result or matches_list


@input_error
def find_phone_record(user_data=None) -> list:

    if not check_params(user_data):
        raise TypeError("NoSuchRecord")
    
    result = find_records(user_data[1:])

    if result == False:
        raise TypeError("NoSuchRecord")
    
    return [user_data[0], result, user_data[1]]


def get_command_handler(command):
    return commands[command][0]


def main() -> None:

    global phones
    phones = {}
    
    while True:

        user_input = input("> ")
        user_data = parse_user_input(user_input)

        if user_data[0]:
            user_data[0] = user_data[0].lower()

        command = user_data[0]
        command_handler = None
        command_result = None

        if command in commands:

            command_handler = get_command_handler(command)
            command_result = command_handler(user_data)

        else:
            if command != False:
                if not command_result:
                    command_result = [False, "NotAValidCommand", *user_data]
            else:
                command_result = user_data

        # Готуємо повідомлення для користувача за результатами виконання команди
        command = command_result[0]

        if command == False:
            # Якщо була помилка - беремо текст з словника
            msg = errors_list[command_result[1]] + "\nCheck your data and repeat or type 'help' for help."

        else:
            # При успішному виконанні в залежності від команди формуємо повідомлення
            match command:

                case "add" | "change" | "delete":
                    msg = f"Record ({command_result[1][0]}: {restore_phone_format(command_result[1][1])}) was {success_list[command]} successfully."

                case "help" | "hello" | "phone" | "showall" | "." | "close" | "exit" | "goodbye" | "quit":

                    if isinstance(command_result[1], list):

                        msg = success_list[command]

                        for i in command_result[1]:
                            msg += i + "\n"
                            
                        msg = msg[:-1]

                    else:
                        msg = command_result[1]

        # Друкуємо повідомлення
        print(msg)

        if command in (".", "close", "exit", "goodbye", "quit"):
            quit()


@input_error
def parse_user_input(user_input) -> list:

    result = user_input.split()
    if len(result) == 0:
        raise TypeError("EmptyInput")

    return result


def quit_bot(user_data=None) -> list:
    return [user_data[0], "\nGood bye!\n"]


def reset_phone_format(phone) -> str:
    return sub(r"[^0-9]", "", phone)


def restore_phone_format(phone) -> str:
    return f"+{phone[:3]}({phone[3:5]}){phone[5:8]}-{phone[8:10]}-{phone[10:]}"


def say_hello(user_data=None) -> str:
    return [user_data[0], "How can I help you?"]


@input_error
def show_all_phone_records(user_data=None) -> list:

    result = []

    if phones:
        for num, item in enumerate(phones):
            result.append(f"{str(num) + '.':<3} {item:<10} {restore_phone_format(phones[item])}")
    else:
        raise TypeError("PhoneListIsEmpty")
    
    return [user_data[0], result]


def show_help(user_data=None) -> str:

    help_str = """
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
    """

    return [user_data[0], help_str]


# Цифра після назви функції - кількість параметрів, які приймає ця функція (разом з іменем функції)
commands = {
    "add": (add_phone_record, 3),
    "change": (change_phone_record, 3),
    "close": (quit_bot, 1),
    "delete": (delete_phone_record, 2),
    "exit": (quit_bot, 1),
    "goodbye": (quit_bot, 1),
    "help": (show_help, 1),
    "hello": (say_hello, 1),
    "phone": (find_phone_record, 2),
    "quit": (quit_bot, 1),
    "showall": (show_all_phone_records, 1),
    ".": (quit_bot, 1)
}

errors_list = {
    "TooManyParameters": "Too many parameters.",
    "TooFewParameters": "Too few parameters.",
    "WrongPhone": "Wrong phone. It must contain 12 digits.",
    "RecordAlreadyExists": "Record with such username already exists.",
    "WrongUserName": "Wrong user name. It cannot consist solely of numbers.",
    "PhoneListIsEmpty": "Phone list is empty.",
    "NoSuchRecord": "No such record(s).",
    "WrongRecordNumber": "Wrong record number.",
    "EmptyInput": "Empty input.",
    "NotAValidCommand": "Not a valid command."
}

success_list = {
    "add": "added",
    "change": "changed",
    "delete": "deleted",
    "phone": "Record(s) that match your query:\n",
    "showall": "All records in the phone book:\n"
}


if __name__ == "__main__":
    main()