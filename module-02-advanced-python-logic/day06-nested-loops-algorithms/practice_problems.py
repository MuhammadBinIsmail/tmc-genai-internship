"""Day 6 - Nested Loops & Algorithmic Logic: practice_problems.py"""

def two_sum(nums, target):
    """Return indices of two numbers that add up to target."""
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None

def caesar_cipher(text, shift):
    """Encode text using a Caesar cipher shift."""
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

def is_valid_sudoku(board):
    """Check if a 9x9 Sudoku board is valid (rows, columns, 3x3 boxes)."""
    for row in board:
        nums = [n for n in row if n != 0]
        if len(nums) != len(set(nums)):
            return False

    for col in range(9):
        nums = [board[row][col] for row in range(9) if board[row][col] != 0]
        if len(nums) != len(set(nums)):
            return False

    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            nums = []
            for i in range(3):
                for j in range(3):
                    val = board[box_row + i][box_col + j]
                    if val != 0:
                        nums.append(val)
            if len(nums) != len(set(nums)):
                return False

    return True

def longest_common_subsequence(a, b):
    """Return the length and value of the longest common subsequence of two strings."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    seq = ""
    i, j = m, n
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            seq = a[i - 1] + seq
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return dp[m][n], seq

def dijkstra(graph, source):
    """Return shortest distances from source using an adjacency matrix (0 = no edge)."""
    n = len(graph)
    distances = [float("inf")] * n
    distances[source] = 0
    visited = [False] * n

    for _ in range(n):
        min_dist = float("inf")
        u = -1
        for i in range(n):
            if not visited[i] and distances[i] < min_dist:
                min_dist = distances[i]
                u = i

        if u == -1:
            break
        visited[u] = True

        for v in range(n):
            if graph[u][v] != 0 and not visited[v]:
                new_dist = distances[u] + graph[u][v]
                if new_dist < distances[v]:
                    distances[v] = new_dist

    return distances

def run_two_sum():
    nums = list(map(int, input("Enter numbers (space-separated): ").split()))
    target = int(input("Enter target sum: "))
    print("Indices:", two_sum(nums, target))

def run_caesar_cipher():
    text = input("Enter text to encode: ")
    shift = int(input("Enter shift value: "))
    print("Encoded:", caesar_cipher(text, shift))

def run_sudoku_validator():
    print("Enter 9 rows, each as 9 space-separated numbers (0 = empty):")
    board = [list(map(int, input(f"Row {i + 1}: ").split())) for i in range(9)]
    print("Valid Sudoku board?", is_valid_sudoku(board))

def run_lcs():
    a = input("Enter first string: ")
    b = input("Enter second string: ")
    length, seq = longest_common_subsequence(a, b)
    print(f"LCS length: {length}, sequence: '{seq}'")

def run_dijkstra():
    n = int(input("Enter number of nodes: "))
    print(f"Enter the {n}x{n} adjacency matrix (0 = no edge), row by row:")
    graph = [list(map(int, input(f"Row {i + 1}: ").split())) for i in range(n)]
    source = int(input("Enter source node index: "))
    print("Shortest distances from source:", dijkstra(graph, source))

def show_menu():
    print("\n--- Practice Problems ---")
    print("1. Two Sum")
    print("2. Caesar Cipher")
    print("3. Sudoku Validator")
    print("4. Longest Common Subsequence")
    print("5. Dijkstra's Shortest Path")
    print("6. Exit")

def main():
    while True:
        show_menu()
        choice = input("Select an option (1-6): ").strip()

        match choice:
            case "1":
                run_two_sum()
            case "2":
                run_caesar_cipher()
            case "3":
                run_sudoku_validator()
            case "4":
                run_lcs()
            case "5":
                run_dijkstra()
            case "6":
                print("Exited!")
                break
            case _:
                print("Invalid choice, please select 1-6.")

if __name__ == "__main__":
    main()