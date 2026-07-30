def km_to_miles(km):
    return km * 0.621371

def miles_to_km(miles):
    return miles / 0.621371

def celsius_to_fahrenheit(c):
    return (c * 9/5) + 32

def fahrenheit_to_celsius(f):
    return (f - 32) * 5/9

def calculate_bmi(weight_kg, height_m):
    return weight_kg / (height_m ** 2)

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def main():
    print("--- Unit & BMI Converter ---")

    km = float(input("\nEnter distance in km: "))
    miles = km_to_miles(km)
    print(f"{km} km = {miles:.2f} miles")

    celsius = float(input("\nEnter temperature in Celsius: "))
    fahrenheit = celsius_to_fahrenheit(celsius)
    print(f"{celsius}°C = {fahrenheit:.1f}°F")

    weight = float(input("\nEnter your weight in kg: "))
    height = float(input("Enter your height in meters: "))
    bmi = calculate_bmi(weight, height)
    category = get_bmi_category(bmi)
    print(f"Your BMI is {bmi:.1f} ({category})")

    is_normal = 18.5 <= bmi < 25
    print(f"\nIs your BMI in the normal range? {is_normal}")


if __name__ == "__main__":
    main()