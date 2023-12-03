# AI Scheduler Bot for Discord

This AI Scheduler Bot utilizes natural language processing to manage events and tasks through Discord, automating calendar management with CalDav. It enables users to interact with their calendar using conversational language.

## Technologies

- **Python**: The primary programming language used.
- **Discord.py**: A Python library to interact with Discord's API.
- **CalDav**: An Internet standard allowing a client to access scheduling information on a remote server.
- **OpenAI**: Leveraged for natural language understanding and processing.
- **icalendar**: Used for iCal format parsing in Python.

## Installation

### Prerequisites

- Python 3.6 or higher
- A Discord account and a bot created on the Discord developer portal
- Access to a CalDav server
- An OpenAI API key

### Setup

1. Clone the repository to your local machine:

```sh
git clone https://github.com/yourusername/ai-scheduler-discord-bot.git
cd ai-scheduler-discord-bot
```

2. Install the required dependencies:

```sh
pip install -r requirements.txt
```

### Configuration

1. Copy or rename `.env.example` to `.env`:

```sh
cp .env.example .env
```

2. Fill in the `.env` file with the necessary details:

```plaintext
# .env file
DISCORD_TOKEN=<Your Discord Bot Token>
OPENAI_API_KEY=<Your OpenAI API Key>
CALDAV_SERVER=<Your CalDav Server URL>
CALDAV_USER=<Your CalDav Username>
CALDAV_PASSWORD=<Your CalDav Password>
```

- `DISCORD_TOKEN` is the token for your Discord bot, obtained from the Discord developer portal.
- `OPENAI_API_KEY` is your API key from OpenAI.
- `CALDAV_SERVER`, `CALDAV_USER`, and `CALDAV_PASSWORD` are your credentials for the CalDav server.

Make sure to replace the placeholders with your actual credentials. This information is sensitive, so never commit your `.env` file to version control.

### Running the Bot

To start the bot, run:

```sh
python bot.py
```

## Usage

After running the bot, you can interact with it in Discord. Use the `!schedule` command followed by the event details in natural language, and the bot will handle the rest.

## Contributing

If you'd like to contribute, please fork the repository and create a pull request with your changes.

## License

This project is open-sourced under the [MIT License](https://choosealicense.com/licenses/mit/).
```
