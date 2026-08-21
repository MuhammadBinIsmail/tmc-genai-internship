"""Day 6 - Nested Loops & Algorithmic Logic: patterns.py"""

def print_pyramid(rows):
    for i in range(1, rows + 1):
        print(" " * (rows - i) + "*" * (2 * i - 1))

def print_right_triangle(rows):
    for i in range(1, rows + 1):
        print("*" * i)

def transpose_matrix(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    result = [[0] * rows for _ in range(cols)]
    for i in range(rows):
        for j in range(cols):
            result[j][i] = matrix[i][j]
    return result

def prime_sieve(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for num in range(2, int(limit ** 0.5) + 1):
        if is_prime[num]:
            for multiple in range(num * num, limit + 1, num):
                is_prime[multiple] = False
    return [num for num, prime in enumerate(is_prime) if prime]

def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

def bubble_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def get_matrix():
    rows = int(input("Enter number of rows: "))
    cols = int(input("Enter number of columns: "))
    matrix = []
    print(f"Enter each row as {cols} space-separated numbers:")
    for i in range(rows):
        row = list(map(int, input(f"Row {i + 1}: ").split()))
        matrix.append(row)
    return matrix

def main():
    rows = int(input("Enter number of rows for pyramid: "))
    print_pyramid(rows)

    rows = int(input("\nEnter number of rows for triangle: "))
    print_right_triangle(rows)

    print("\nEnter a matrix to transpose:")
    matrix = get_matrix()
    print("Transpose:")
    for row in transpose_matrix(matrix):
        print(row)

    limit = int(input("\nFind primes up to: "))
    print(prime_sieve(limit))

    nums = list(map(int, input("\nEnter numbers for search/sort (space-separated): ").split()))
    target = int(input("Enter number to search for: "))
    print("Index found at:", linear_search(nums, target))
    print("Sorted:", bubble_sort(nums.copy()))

if __name__ == "__main__":
    main()