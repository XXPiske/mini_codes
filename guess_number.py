import random

def get_int_from_input(user_input: str) -> int | None:
    try:
        user_number = int(user_input)
        return user_number
    except ValueError:
        return None

def main():
    the_chosen_number = random.randint(1,100)
    while True:
        user_input = input('Take a guess 1 to 100: ')
        user_number = get_int_from_input(user_input)
        if user_number is None:
            print('Error: Use integer!')
            continue
        elif user_number < 1 or user_number > 100:
            print('Error: Out of range! Use number from 1 to 100')
            continue
        
        if user_number == the_chosen_number:
            print(f"You won! The number was: {the_chosen_number}")
            break
        elif user_number > the_chosen_number:
            print('Smaller')
        else:
            print('Bigger')
   
if __name__ == '__main__':
    main()