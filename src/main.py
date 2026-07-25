import os
import json
import threading

from flask import Flask, send_from_directory
from dotenv import load_dotenv
from openai import OpenAI

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

from utils import extract_url
from data_tools import load_dataset
from analyzer import basic_analysis
from logger import write_log

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
AIPIPE_TOKEN = os.getenv("AIPIPE_TOKEN")

client = OpenAI(
    api_key=AIPIPE_TOKEN,
    base_url="https://aipipe.org/openai/v1"
)

conversation_history = {}

flask_app = Flask(__name__)


@flask_app.route("/")
def health():
    return "Bot is running"


@flask_app.route("/run.jsonl")
def serve_log():
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "run.jsonl")

    # Create the file if it doesn't exist yet
    if not os.path.exists(log_file):
        open(log_file, "a").close()

    return send_from_directory(
        log_dir,
        "run.jsonl",
        mimetype="application/json"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.chat_id
    question = update.message.text

    analysis_result = None
    dataset_info = ""

    url = extract_url(question)

    if url:
        try:
            df = load_dataset(url)

            dataset_info = (
                f"Dataset loaded.\n"
                f"Rows: {len(df)}\n"
                f"Columns: {list(df.columns)}"
            )

            analysis_result = basic_analysis(df, question)

        except Exception as e:
            dataset_info = f"Dataset error: {str(e)}"

    if user_id not in conversation_history:
        conversation_history[user_id] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful data analyst. "
                    "Return accurate answers."
                ),
            }
        ]

    prompt = f"""
Question:
{question}

Dataset:
{dataset_info}

Analysis:
{analysis_result}
"""

    conversation_history[user_id].append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history[user_id],
    )

    answer = response.choices[0].message.content

    conversation_history[user_id].append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    write_log(question, answer)

    result = {
        "answer": answer,
        "log_url": os.getenv("LOG_URL", ""),
    }

    await update.message.reply_text(json.dumps(result))


def main():

    threading.Thread(
        target=lambda: flask_app.run(
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 10000)),
            use_reloader=False,
        ),
        daemon=True,
    ).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    print("AI Data Analyst Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()
