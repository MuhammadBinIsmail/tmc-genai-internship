"""Day 7 - Comprehensions, Lambdas & Error Handling"""

class NegativeValueError(Exception):
    """Raised when a negative number is entered where not allowed."""
    pass

def get_number_list():
    """Prompt for a space-separated list of numbers."""
    raw = input("Enter numbers (space-separated): ").split()
    return [int(n) for n in raw]

def demo_comprehensions():
    nums = get_number_list()

    squares = [n ** 2 for n in nums]
    print("Squares (list comprehension):", squares)

    evens_only = [n for n in nums if n % 2 == 0]
    print("Evens only:", evens_only)

    square_map = {n: n ** 2 for n in nums}
    print("Number -> square (dict comprehension):", square_map)

    unique_remainders = {n % 3 for n in nums}
    print("Unique remainders mod 3 (set comprehension):", unique_remainders)

    gen = (n ** 2 for n in nums)
    print("Generator expression sum of squares:", sum(gen))

def demo_lambda_map_filter():
    nums = get_number_list()

    doubled = list(map(lambda n: n * 2, nums))
    print("Doubled (map + lambda):", doubled)

    positives = list(filter(lambda n: n > 0, nums))
    print("Positives only (filter + lambda):", positives)

    words = input("Enter some words (space-separated): ").split()
    sorted_by_length = sorted(words, key=lambda w: len(w))
    print("Sorted by length:", sorted_by_length)

    for index, word in enumerate(words):
        print(f"{index}: {word}")

    numbers_for_zip = get_number_list()
    if len(numbers_for_zip) == len(words):
        pairs = list(zip(words, numbers_for_zip))
        print("Zipped word/number pairs:", pairs)
    else:
        print("Skipping zip demo - word and number counts don't match.")

def get_positive_number():
    """Get a number from the user, raising a custom exception if negative."""
    value = int(input("Enter a positive number: "))
    if value < 0:
        raise NegativeValueError(f"{value} is negative, expected a positive number.")
    return value

def demo_error_handling():
    try:
        value = get_positive_number()
    except ValueError:
        print("That wasn't a valid number.")
    except NegativeValueError as e:
        print(f"Custom error caught: {e}")
    else:
        print(f"Success, you entered: {value}")
    finally:
        print("Input attempt finished.")

def demo_input_validation():
    while True:
        try:
            age = int(input("Enter your age: "))
            if age <= 0 or age > 120:
                raise ValueError("Age must be between 1 and 120.")
        except ValueError as e:
            print(f"Invalid input: {e}. Try again.")
            continue
        else:
            print(f"Age accepted: {age}")
            break

def show_menu():
    print("\n--- Pythonic Concepts ---")
    print("1. Comprehensions & Generators")
    print("2. Lambda, Map, Filter, Sorted, Enumerate, Zip")
    print("3. Error Handling (try/except/else/finally, custom exception)")
    print("4. Robust Input Validation")
    print("5. Exit")

def main():
    while True:
        show_menu()
        choice = input("Select an option (1-5): ").strip()

        match choice:
            case "1":
                demo_comprehensions()
            case "2":
                demo_lambda_map_filter()
            case "3":
                demo_error_handling()
            case "4":
                demo_input_validation()
            case "5":
                print("Goodbye!")
                break
            case _:
                print("Invalid choice, please select 1-5.")

if __name__ == "__main__":
    main()