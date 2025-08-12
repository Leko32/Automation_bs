# Blue Sky Automation

This is a **Python automation tool** that opens multiple browser profiles, scrolls infinitely through followers on a specified website, and automatically follows them.  
It can handle multiple accounts in parallel and send you Telegram notifications if it reaches the end of the followers list or encounters any errors.

---

## 🚀 Features
- Runs multiple browser profiles at once
- Logs in automatically if needed
- Infinite scrolling through followers
- Customizable:
  - Number of follows per cycle
  - Timeout between cycles
- Telegram bot integration for notifications
- Error logging

---

## 📥 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Leko32/Automation_bs
   cd Automation_bs

    Install dependencies

    pip install -r requirements.txt
   
# ⚙️ Setup
**1. Create profiles**

Inside the profiles folder, create the required number of profile folders in the format:
     
      profiles/
        profile_1/
        profile_2/
        ...

**2. Configure credentials**

Edit the creds.json file and add your accounts:

    {
      "profile_1": {
        "login": "your_username",
        "password": "your_password",
        "url": "https://example.com/profile"
      },
      "profile_2": {
        "login": "second_username",
        "password": "second_password",
        "url": "https://example.com/another-profile"
      }
    }

**3. Set up Telegram notifications**

In the notify.py file:

    Set your Telegram Bot Token

    Set your Chat ID

# ▶️ Usage

Run the script:

python main.py

The script will:

    Launch the specified number of browsers

    Log in if needed

    Scroll through followers and follow them

    Wait for the specified timeout after each cycle

    Send Telegram messages when:

        It reaches the end of the follower list

        An error occurs

# 📝 Logs

Logs are stored in the logs folder:

    bug.log — errors during execution

    finish.log — when a profile reaches the end of the followers list

# ⚠️ Disclaimer

This project is for educational purposes only.
Using automated tools on websites may violate their terms of service. Use at your own risk.

