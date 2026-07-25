from flask import Flask, send_file

app = Flask(__name__)


@app.route("/run.jsonl")
def logs():
    return send_file(
        "../logs/run.jsonl",
        mimetype="application/json"
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )
