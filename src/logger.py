import json
import os
from datetime import datetime


LOG_FILE = "logs/run.jsonl"


def write_log(question, answer):

    os.makedirs("logs", exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "answer": answer
    }

    with open(LOG_FILE, "a") as f:
        f.write(
            json.dumps(entry)
            + "\n"
        )
