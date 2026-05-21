import random
from datetime import datetime, timedelta

def get_int_from_input(user_input: str) -> int | None:
    try:
        user_number = int(user_input)
        return user_number
    except ValueError:
        return None

def format_time(td: timedelta) -> str:
    total_seconds = int(td.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    str_minutes = "minutes" if minutes > 1 else "minute"
    str_seconds = "seconds" if seconds > 1 else "second"
    if minutes:
        return f"{minutes} {str_minutes} and {seconds} {str_seconds}"
    else:
        return f"{seconds} {str_seconds}"

def set_range() -> tuple[int, int]:
    while True:
        left_bound = input('Set left guessing bound: ')
        left_int_bound = get_int_from_input(left_bound)
        if left_int_bound is None:
            print('Error: Use integer!')
            continue
        else:
            break
    while True:
        right_bound = input('Set right guessing bound: ')
        right_int_bound = get_int_from_input(right_bound)
        if right_int_bound is None:
            print('Error: Use integer!')
            continue
        else:
            if right_int_bound <= left_int_bound:
                print('Error: Right bound must be bigger than Left bound!')
                continue
            else:
                break
    return left_int_bound, right_int_bound

def restart() -> bool:
    while True:
        ask = input("Type 'y' to start again and 'n' to end the game: ")
        if ask == 'y':
            return True
        if ask == 'n':
            return False

def main():
    while True:
        left_int_bound, right_int_bound = set_range()
        the_chosen_number = random.randint(left_int_bound,right_int_bound)
        attempt = 1
        start_time = datetime.now()
        while True:
            user_input = input(f'Take a guess from {left_int_bound} to {right_int_bound}: ')
            user_number = get_int_from_input(user_input)
            if user_number is None:
                print('Error: Use integer!')
                continue
            elif user_number < left_int_bound or user_number > right_int_bound:
                print(f'Error: Out of range! Use number from {left_int_bound} to {right_int_bound}')
                continue
                        
            if user_number == the_chosen_number:
                end_time = datetime.now()
                total_time = (end_time - start_time)
                total_time_formatted = format_time(total_time)
                print(f"You won! The number was: {the_chosen_number}\nAttempts: {attempt}\nTime: {total_time_formatted}")
                break
            elif user_number > the_chosen_number:
                print('Smaller')
                attempt = attempt + 1
            else:
                print('Bigger')
                attempt = attempt + 1
        if restart():
            continue
        else:
            break
   
if __name__ == '__main__':
    main()
