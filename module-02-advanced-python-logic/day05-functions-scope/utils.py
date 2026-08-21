"""
Day 5 - Functions, Scope & Arguments
utils.py - reusable functions with docstrings
"""

def add(a: float, b: float) -> float:
    return a + b

def subtract(a: float, b: float) -> float:
    return a - b

def km_to_miles(km: float) -> float:
    return km * 0.621371

def celsius_to_fahrenheit(c: float) -> float:
    return (c * 9/5) + 32

def calculate_bmi(weight: float, height: float) -> float:
    """Calculate BMI given weight in kg and height in meters."""
    return weight / (height ** 2)

def count_words(text: str) -> dict:
    """Count how many times each word appears in a string."""
    words = text.lower().split()
    counts = {}
    for word in words:
        word = word.strip(".,!?")
        if word:
            counts[word] = counts.get(word, 0) + 1
    return counts

def add_numbers(*args, label="Sum"):
    """Add any number of arguments together and print the result."""
    total = sum(args)
    print(f"{label}: {total}")
    return total

def make_profile(name, **details):
    """Build a dictionary profile from a name and extra keyword details."""
    profile = {"name": name}
    profile.update(details)
    return profile

counter = 0

def increment():
    """Increase the global counter by 1."""
    global counter
    counter += 1
    return counter

def local_scope_demo(x, y):
    """Show that variables inside a function don't affect outside code."""
    result = x + y
    return result

if __name__ == "__main__":
    print(add(5, 3))
    print(subtract(10, 4))
    print(km_to_miles(50))
    print(celsius_to_fahrenheit(30))
    print(calculate_bmi(65, 1.7))
    print(count_words("hello world hello python"))
    add_numbers(1, 2, 3, label="Total")
    print(make_profile("Ali", age=21, city="Karachi"))
    print(increment())
    print(increment())
    print(local_scope_demo(4, 5))