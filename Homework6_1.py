import pickle
import re
from datetime import datetime, timedelta


# створюємо клас для управління адресною книгою
class Field:
    def __init__(self, value):
        self.value = value
    # метод перетворює обєкт класу у рядок 
    def __str__(self):
        return str(self.value)

# клас призначений для зберігання імені контакту
class Name(Field):
    def __init__(self, value):
        super().__init__(value)


# клас призначений для зберігання номеру телефону
class Phone(Field):
    def __init__(self, value):
        self._validate_phone(value)
        super().__init__(value)
    # перевірка чи введено 10 значний номер телефону за допомогою регулярного виразу
    def _validate_phone(self, value):
       if not re.fullmatch(r"\d{10}", value):
          raise ValueError("Phone number must be exactly 10 digits")

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value,"%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")    


# Клас призначений для зберігання та управління інформацією про контакт
class Record:

    # зберігає імя контакту в порожній список - self.phones = []
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # додає новий номер телефону до списку
    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    # перебирає всі телефони у списку та видаляє номер телефону який буде переданий
    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                break

    # редагує існуючий телефон замінюючи на новий
    def edit_phone(self, old_number, new_number):
        for phone in self.phones:
            if phone.value == old_number:
                phone.value = new_number
                break

    # знаходить і повертає об'єкт з номером
    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
    
    # додає день народження до списку
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
        
    # повертає рядкове представлення об'єкта
    def __str__(self):
        phones = '; '.join(phone.value for phone in self.phones)
        birthday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday_str}"
# створенмо клас для управління колекцією контактів
class AddressBook():
    def __init__(self):
        self.records = {}
    # додає новий контактний запис до адресної книги.
    def add_record(self, record):
        self.records[record.name.value] = record
    # знаходить і повертає запис контакту за його ім'ям
    def find(self, name):
        return self.records.get(name)
    # видаляє запис контакту за його ім'ям
    def delete(self, name):
        if name in self.records:
            del self.records[name]
    # повертає список користувачів, яких потрібно привітати по днях на наступному тижні
    def get_upcoming_birthdays(self, days=7):
        today =datetime.today()
        upcoming_birthdays = []
        for record in self.records.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if today <= birthday_this_year < today + timedelta(days=days):
                    upcoming_birthdays.append(record)
        return upcoming_birthdays            

    def list_all_contacts(self):
        return self.records.values()





def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Error: Contact not found."
        except ValueError:
            return "Error: Please provide: <name> <phone>. Phone number must be exactly 10 digits."
        except IndexError:
            return "Error: No arguments provided. Please provide <name>."
    return inner



@input_error
# додаємо функцію яка приймає рядок вводу користувача і розбиває його на слова - метод split()
def parse_input(user_input):
    cmd, *args = user_input.split()
    # видаляємо зайві пробіли та перетворюємо на нижній регістр.
    cmd = cmd.strip().lower()     
    return cmd, *args
    

@input_error
# додаємо функцію яка додає пару "ключ: значення" до словника контактів, 
# використовуючи ім'я як ключ і телефонний номер як значення
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated"
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added"
    if phone:
        record.add_phone(phone)
    return message        


@input_error
# додаємо функцію яка замінює телефонний номер для контакту який вже був створений
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record and record.change_phone(old_phone, new_phone):
        return "Contact update"
    return "Erorr: Old phone number not found."
    

@input_error
# додаємо функцію яка виводить телефонний номер за введеним контактом
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        phones = ', '.join(phone.value for phone in record.phones)
        return f"{name}: {phones}"
    else:
        return "Error: Contact not found."


# додаємо функцію яка виводить всі збережені контактиadd wewew 121212
def show_all(book: AddressBook):
    if not book.records:
        return "No contacts found."
    return "\n".join(
        f"Name {record.name.value}: {', '.join(phone.value for phone in record.phones)}, birthday:{record.birthday.value.strftime('%d.%m.%Y')}"
        for record in book.list_all_contacts()) 


# додаємо функцію яка додає день народження до створеного контакту
@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    # перевіряємо чи існує контакт
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    return "Error: Contact not found."


# додаємо функцію яка виводить день народження  за введеним контактом
@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}."
    return "Error: Birthday not found for this contact."


# додаємо функцію яка виводить всі прийдешні дні наподження протягом 7 днів
@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(
        f"{record.name.value}: {record.birthday.value.strftime('%d.%m')}"
        for record in upcoming
    )

def save_data(book, filename = "addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book,f)

def load_data(filename = "adressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

# додаємо функцію яка входить в нескінчений цикл і очікує введення команди
def main():
    book = load_data()   # додаємо словник для контактів
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        if not user_input:
            continue
        
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break    
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))   
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))                   
        else:
            print("Invalid command.Provide correct command")

if __name__ == "__main__":
    main()