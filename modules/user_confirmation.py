# modules/user_confirmation.py

def confirm_email(generated_email: str) -> bool:
    print("\n📧 Generated Email:\n")
    print(generated_email)
    
    user_input = input("\nDo you want to send this email? (yes/no): ").lower()
    return user_input in ["yes", "y"]

