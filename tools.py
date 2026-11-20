"""Tools for the BrezyWeather support agent: an open set and a least-privilege set."""
import json
from pathlib import Path

HERE = Path(__file__).parent
ACCOUNTS = json.loads((HERE / "accounts.json").read_text())


def schema(name, description, **params):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {p: {"type": "string"} for p in params},
                "required": list(params),
                "additionalProperties": False,
            },
        },
    }


# ── Read tools ────────────────────────────────────────────────────────────────

def get_ticket(ticket_id):
    return (HERE / "tickets" / f"{ticket_id}.md").read_text()


def get_account(account_id):
    return json.dumps(ACCOUNTS[account_id])


def get_account_public(account_id):
    # Least privilege: the API key never leaves this function
    record = dict(ACCOUNTS[account_id])
    record.pop("api_key")
    return json.dumps(record)


# ── Action tools ──────────────────────────────────────────────────────────────

def send_email(to, subject, body):
    print(f"  EMAIL SENT to {to}\n    subject: {subject}\n    body: {body}")
    return "sent"


def reply_to_customer(account_id, message):
    # Least privilege: the recipient comes from the account, never from the model
    to = ACCOUNTS[account_id]["email"]
    print(f"  REPLY SENT to {to}")
    return f"sent to {to}"


# ── Tool sets ─────────────────────────────────────────────────────────────────

OPEN_TOOLS = {
    "get_ticket": (get_ticket, schema("get_ticket", "Read a support ticket.", ticket_id="")),
    "get_account": (get_account, schema("get_account", "Read a customer account record.", account_id="")),
    "send_email": (send_email, schema("send_email", "Send an email.", to="", subject="", body="")),
}

SCOPED_TOOLS = {
    "get_ticket": OPEN_TOOLS["get_ticket"],
    "get_account": (get_account_public, schema("get_account", "Read a customer account record.", account_id="")),
    "reply_to_customer": (reply_to_customer, schema(
        "reply_to_customer", "Email the account's customer at their address on file.", account_id="", message="")),
}

ACTION_TOOLS = {"send_email", "reply_to_customer"}
