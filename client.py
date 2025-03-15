import requests
import os

BASE_URL = "http://127.0.0.1:8000/api"
TOKEN_FILE = "token.txt"


def save_token(token):
    with open(TOKEN_FILE, "w") as file:
        file.write(token)


def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            return file.read().strip()
    return None


def delete_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)


def register():
    """Handles user registration."""
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")

    response = requests.post(f"{BASE_URL}/register/", json={
        "username": username,
        "email": email,
        "password": password
    })

    if response.status_code == 201:
        print("✅ Registration successful!")
    else:
        print("❌ Registration failed:", response.status_code, response.json())


def login():
    """Handles user login."""
    username = input("Enter username: ")
    password = input("Enter password: ")

    response = requests.post(f"{BASE_URL}/login/", json={
        "username": username,
        "password": password
    })

    if response.status_code == 200:
        token = response.json().get("token")
        save_token(token)
        print("✅ Login successful!")
        return True
    else:
        print("❌ Login failed:", response.json())
        return False


def logout():
    """Handles user logout and returns to the authentication menu."""
    token = load_token()
    if not token:
        print("⚠️ You are not logged in.")
        return

    response = requests.post(f"{BASE_URL}/logout/", headers={"Authorization": f"Token {token}"})
    
    if response.status_code == 200:
        delete_token()
        print("✅ Logged out successfully!")
    else:
        print("❌ Logout failed:", response.json())


def list_modules():
    """Fetch and display all module instances including professors, year, and semester."""
    token = load_token()
    headers = {"Authorization": f"Token {token}"} if token else {}

    response = requests.get(f"{BASE_URL}/modules/", headers=headers)

    if response.status_code == 200:
        modules = response.json()
        print("\n📚 Module List:")
        for module in modules:
            print(f"📌 {module['code']} - {module['name']} ({module['year']}, Semester {module['semester']})")
            print("   Taught by:", ", ".join([f"{prof['name']} ({prof['id']})" for prof in module['professors']]))
            print("-" * 50)
    else:
        print("❌ Failed to fetch modules:", response.status_code, response.json())


def view_all_professor_ratings():
    """Fetch and display all professors with their ratings and the modules they handle."""
    token = load_token()
    headers = {"Authorization": f"Token {token}"} if token else {}

    response = requests.get(f"{BASE_URL}/professors/", headers=headers)

    if response.status_code == 200:
        try:
            professors = response.json()
            if not professors:  # Handle empty response
                print("⚠️ No professors found in the system.")
                return

            print("\n🎓 Professor Ratings:\n")
            for prof in professors:
                prof_id = prof["id"]
                prof_name = prof["name"]
                avg_rating = prof["average_rating"]

                # Fetch modules this professor teaches
                modules_response = requests.get(f"{BASE_URL}/modules/", headers=headers)
                modules = []
                if modules_response.status_code == 200:
                    try:
                        all_modules = modules_response.json()
                        for module in all_modules:
                            if any(teacher["id"] == prof_id for teacher in module["professors"]):
                                modules.append(f"{module['name']} ({module['code']})")
                    except requests.exceptions.JSONDecodeError:
                        print("⚠️ Server error: Failed to parse module list.")

                module_list = ", ".join(modules) if modules else "No modules assigned"
                print(f"👨‍🏫 {prof_name} (ID: {prof_id})")
                print(f"   📊 Rating: {avg_rating}")
                print(f"   📚 Modules: {module_list}\n")
                print("-" * 50)

        except requests.exceptions.JSONDecodeError:
            print("⚠️ Server returned an empty response or invalid JSON format.")
    else:
        print(f"❌ Failed to fetch professor ratings (HTTP {response.status_code})")


def average_rating():
    """View the average rating of a certain professor in a certain module instance."""
    token = load_token()
    if not token:
        print("⚠️ You must be logged in to view ratings.")
        return

    professor_id = input("Enter professor ID (e.g., 1,2): ").strip()
    module_code = input("Enter module code (e.g., CS3021): ").strip()
    year = input("Enter year (e.g., 2024): ").strip()
    semester = input("Enter semester (1 or 2): ").strip()

    headers = {"Authorization": f"Token {token}"}
    params = {"year": year, "semester": semester}  # Pass year & semester as query params

    response = requests.get(f"{BASE_URL}/ratings/{professor_id}/{module_code}/", headers=headers, params=params)

    if response.status_code == 200:
        try:
            data = response.json()

            # Extract necessary fields safely
            professor_name = data.get("professor_name", f"Professor {professor_id}")
            module_name = data.get("module_name", f"Module {module_code}")
            avg_rating = data.get("average_rating", "No ratings yet")

            # Convert rating to stars only if it's a number
            if isinstance(avg_rating, (int, float)):  
                avg_rating = round(avg_rating)
                stars = "⭐" * avg_rating
            else:
                stars = "No ratings yet"

            # Print formatted output
            print("\n📊 Professor Rating Summary")
            print(f"👨‍🏫 Professor: {professor_name} (ID: {professor_id})")
            print(f"📚 Module: {module_name} (Code: {module_code})")
            print(f"📅 Year: {year}, Semester: {semester}")
            print(f"⭐ Average Rating: {stars}\n")

        except requests.exceptions.JSONDecodeError:
            print("⚠️ Server returned an invalid response. Please try again.")
    elif response.status_code == 404:
        print("❌ Invalid professor ID, module code, year, or semester. Please check your input.")
    else:
        print(f"❌ Failed to fetch ratings (HTTP {response.status_code}):", response.text)


def rate_professor():
    """Allows a logged-in user to rate a professor."""
    token = load_token()
    if not token:
        print("⚠️ You must be logged in to rate a professor.")
        return

    professor_id = input("Enter professor ID: ").strip()
    module_code = input("Enter module code: ").strip()
    year = input("Enter year: ").strip()
    semester = input("Enter semester (1 or 2): ").strip()
    rating = input("Enter rating (1-5): ").strip()

    if not rating.isdigit() or not (1 <= int(rating) <= 5):
        print("❌ Invalid rating. Please enter a number between 1 and 5.")
        return

    response = requests.post(f"{BASE_URL}/rate/", json={
        "professor": professor_id,
        "module": module_code,
        "year": year,
        "semester": semester,
        "rating": rating
    }, headers={"Authorization": f"Token {token}"})

    if response.status_code == 201:
        print("✅ Rating submitted successfully!")
    else:
        print(f"❌ Error: {response.json().get('detail', 'Unknown error')}")


def auth_menu():
    """Menu for authentication (Register/Login/Exit)."""
    while True:
        print("\n📌 Authentication Menu: register | login | exit")
        command = input("Enter command: ").strip().lower()

        if command == "register":
            register()
        elif command == "login":
            if login():
                return  # Move user to main menu after login
        elif command == "exit":
            print("👋 Exiting client.")
            exit()
        else:
            print("❌ Invalid command! Please enter 'register', 'login', or 'exit'.")


def main_menu():
    """Main menu after successful login, showing options 1-4."""
    while True:
        print("\n📌 Main Menu (Choose an option):")
        print("1️⃣  List module instances and professors")
        print("2️⃣  View professor ratings")
        print("3️⃣  View average professor rating in a module")
        print("4️⃣  Rate a professor")
        print("🔴  Logout (type 'logout')")

        command = input("Enter option (1-4) or 'logout': ").strip().lower()

        # Options 1-4 
        if command == "1":
            list_modules() 
        elif command == "2":
            view_all_professor_ratings()
        elif command == "3":
            average_rating()
        elif command == "4":
            rate_professor()
        elif command == "logout":
            logout()
            return  # Go back to authentication menu
        else:
            print("❌ Invalid option! Please enter a number (1-4) or 'logout'.")


def main():
    """Start the client application with authentication first."""
    while True:
        auth_menu()  # First menu (only register, login, exit)
        main_menu()  # After login, access main menu

if __name__ == "__main__":
    main()
