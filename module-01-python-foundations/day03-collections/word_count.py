
def count_words(text):
    words = text.lower().split()
    cleaned_words = []
    for word in words:
        cleaned = word.strip(".,!?;:\"'()")
        if cleaned:
            cleaned_words.append(cleaned)
    frequency = {}
    for word in cleaned_words:
        frequency[word] = frequency.get(word, 0) + 1

    return frequency

def main():
    paragraph = input("Enter a paragraph:\n")
    frequency = count_words(paragraph)

    print("\n--- Word Frequency ---")
    for word, count in sorted(frequency.items(), key=lambda x: x[1], reverse=True):
        print(f"{word}: {count}")

    unique_words = set(frequency.keys())
    print(f"\nTotal unique words: {len(unique_words)}")

if __name__ == "__main__":
    main()