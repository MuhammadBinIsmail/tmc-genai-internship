
contacts = {}

def add_contact():
    name = input("Enter name: ").strip()
    phone = input("Enter phone number: ").strip()
    contacts[name] = phone
    print(f"Added: {name} -> {phone}")

def view_contacts():
    if not contacts:
        print("No contacts saved yet.")
        return
    print("\n--- Contact List ---")
    for name, phone in contacts.items():
        print(f"{name}: {phone}")

def update_contact():
    name = input("Enter name to update: ").strip()
    if name in contacts:
        new_phone = input("Enter new phone number: ").strip()
        contacts[name] = new_phone
        print(f"Updated: {name} -> {new_phone}")
    else:
        print(f"'{name}' not found in contacts.")

def delete_contact():
    name = input("Enter name to delete: ").strip()
    if name in contacts:
        del contacts[name]
        print(f"Deleted: {name}")
    else:
        print(f"'{name}' not found in contacts.")

def main():
    while True:
        print("\n--- Contact Book ---")
        print("1. Add Contact")
        print("2. View Contacts")
        print("3. Update Contact")
        print("4. Delete Contact")
        print("5. Exit")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_contact()
        elif choice == "2":
            view_contacts()
        elif choice == "3":
            update_contact()
        elif choice == "4":
            delete_contact()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()