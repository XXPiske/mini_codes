from datetime import datetime

PASSWORD = '123'

def get_time_with_password(password: str) -> str:
    if password == PASSWORD:
        return f"Welcome! Time now: {datetime.now()}"
    else:
        return "Error: the password is wrong"

def start_again():
    while True:
        input_from_user = input('Type "start" to begin again: ')

        if input_from_user == 'start':
            return
        else: None

def main():
    while True:
        pw_from_user = input('Enter the password: ')

        if pw_from_user == 'exit':
            start_again()
            continue

        print(get_time_with_password(pw_from_user))

if __name__ == '__main__':  
    main()