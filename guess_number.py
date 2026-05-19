import random

def main():
    the_chosen_number = random.randint(1,100)
    while True:
        while True:
            try:
                user_number = int(input('Take a guess 1 to 100: '))
                if user_number < 1 or user_number > 100:
                    print('Error: Out of range! Use number from 1 to 100')
                    continue
                break
            except ValueError:
                print('Error: Use integer!')
        if user_number == the_chosen_number:
            print(f"You won! The number was: {the_chosen_number}")
            break
        elif user_number > the_chosen_number:
            print('Smaller')
        else:
            print('Bigger')
   
if __name__ == '__main__':
    main()