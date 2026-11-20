"""Defenses that run outside the model: Prompt Shields and human approval."""
import os

import httpx
from azure.identity import DefaultAzureCredential

ENDPOINT = os.environ["BREZY_AI_ENDPOINT"].rstrip("/")
credential = DefaultAzureCredential()
http = httpx.Client(transport=httpx.HTTPTransport(retries=2))
SHIELD_CHARS = 10_000   # Prompt Shields checks up to 10K characters of documents per call


def shield(user_task, tool_output):
    # Prompt Shields: check the tool output as a document before the model sees it,
    # in 10K-character chunks so a long result is checked in full; any flagged chunk flags it
    token = credential.get_token("https://cognitiveservices.azure.com/.default").token
    for start in range(0, len(tool_output), SHIELD_CHARS):
        response = http.post(
            f"{ENDPOINT}/contentsafety/text:shieldPrompt?api-version=2024-09-01",
            headers={"Authorization": f"Bearer {token}"},
            json={"userPrompt": user_task, "documents": [tool_output[start:start + SHIELD_CHARS]]},
        )
        response.raise_for_status()
        if response.json()["documentsAnalysis"][0]["attackDetected"]:
            return True
    return False


def approve(name, args):
    # Human approval: an action runs only after a person reads it and says yes
    print(f"  APPROVAL NEEDED: {name}")
    for key, value in args.items():
        indented = str(value).replace("\n", "\n      ")
        print(f"    {key}: {indented}")
    return input("  Run it? [y/N] ").strip().lower() == "y"
