# Mittens Bot

Mittens Bot is a Telegram bot designed to help users set and track their goals. It allows users to set weekly goals, log their progress, and receive weekly reports on their achievements.

## Features

- Set up to 4 weekly goals
- Log progress towards goals
- Web app interface for easy goal tracking
- Weekly reports on goal completion
- 4 AM cutoff for logging previous day's goals

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or higher
- pip (Python package installer)
- A Telegram account
- A Telegram Bot Token (obtainable from BotFather)

## Installation

1. Clone this repository or download the source code:

   ```
   git clone https://github.com/yourusername/mittens-bot.git
   cd mittens-bot
   ```

2. Create a virtual environment and activate it:

   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:

   ```
   pip install python-telegram-bot flask
   ```

4. Set up the database:

   ```
   sqlite3 mittens_bot.db < schema.sql
   ```

5. Create a `config.py` file with your bot token and other settings:

   ```python
   BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
   WEBAPP_URL = 'http://localhost:5000'
   DB_NAME = 'mittens_bot.db'
   ```

   Replace 'YOUR_BOT_TOKEN_HERE' with the token you received from BotFather.

## Usage

1. Start the Flask server:

   ```
   export FLASK_APP=mittens_bot.py
   flask run
   ```

2. In a new terminal window, start the bot:

   ```
   python3 mittens_bot.py
   ```

3. Open Telegram and start a conversation with your bot by sending the `/start` command.

4. Use the following commands to interact with the bot:
   - `/start`: Initialize the bot and get the main menu
   - `/set`: Start setting your weekly goals

5. Use the web app interface to log your progress towards goals.

## Project Structure

- `mittens_bot.py`: The main bot script
- `config.py`: Configuration file for bot settings
- `schema.sql`: SQL schema for the database
- `webapp.html`: HTML file for the web app interface

## Customization

You can customize the bot's behavior by modifying the `mittens_bot.py` file. Some areas you might want to customize include:

- The maximum number of goals a user can set
- The format of the weekly report
- The cutoff time for logging goals

## Troubleshooting

If you encounter any issues:

1. Ensure all dependencies are installed correctly
2. Check that your `config.py` file contains the correct bot token
3. Make sure both the Flask server and the bot script are running
4. Check the console output for any error messages

## Contributing

Contributions to the Mittens Bot are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

If you have any questions or feedback, please contact [Your Name] at [yb@yashbhardwaj.com].

Happy goal setting and tracking with Mittens Bot!