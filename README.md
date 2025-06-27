# Hungarian Name Day Telegram Notifier

This service sends a daily Telegram message with the Hungarian name days for the current day and the next day.

## Setup

1.  **Create a Telegram Bot**
    *   Talk to the [BotFather](https://t.me/botfather) on Telegram to create a new bot.
    *   You will get a bot token.

2.  **Get your Chat ID**
    *   Talk to the `@userinfobot` on Telegram to get your user ID. This will be your chat ID.

3.  **Set Environment Variables**
    *   The application reads the following environment variables:
        *   `TELEGRAM_BOT_TOKEN`: Your Telegram bot token.
        *   `TELEGRAM_CHAT_ID`: Your Telegram chat ID.

## Running with Docker

1.  Build the Docker image:
    ```bash
    docker build -t nevnap-service .
    ```

2.  Run the Docker container with your environment variables:
    ```bash
    docker run -d --name nevnap-service \
      -e TELEGRAM_BOT_TOKEN="your_token" \
      -e TELEGRAM_CHAT_ID="your_chat_id" \
      nevnap-service
    ``` 