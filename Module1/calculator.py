def calculator(num1, num2, operator):
    if operator == "+":
        return num1 + num2
    elif operator == "-":
        return num1 - num2
    elif operator == "*":
        return num1 * num2
    elif operator == "/":
        if num2 == 0:
            return "Error: Division by zero"
        return num1 / num2
    else:
        return "Invalid Operator."

num1 = float(input("Enter num1: "))
num2 = float(input("Enter num2: "))
operator = input("Enter Operator (+, -, *, /): ")

result = calculator(num1, num2, operator)
print("\nHello World\n")
print("Result:", result, "\n")
