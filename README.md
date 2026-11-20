# BrezyWeather Support Agent: Prompt Injection Through Tools

Demo files for the Code with Praveen video "Stop Prompt Injection in Your AI Agent's Tools". A small support agent on Azure OpenAI that a planted ticket comment hijacks, and `--defend`, which adds least-privilege tools, a human approval, and Prompt Shields on every tool result.

## Requirements

- An Azure subscription where you can create resources and role assignments
- Azure CLI 2.89.0 or later, signed in with `az login`
- Python 3.10 or later (tested on 3.14.6); packages pinned in `requirements.txt`
- Model `gpt-5.4-mini` (2026-03-17) with Global Standard quota in eastus2

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt   # python3 must be 3.10+; macOS's /usr/bin/python3 is 3.9
RG=rg-brezyweather-support-agent; AI=brezyweather-support-ai-$RANDOM   # account name must be globally unique
az group create -n $RG -l eastus2
az cognitiveservices account create -n $AI -g $RG -l eastus2 --kind AIServices --sku S0 --custom-domain $AI --yes
az cognitiveservices account deployment create -g $RG -n $AI --deployment-name gpt-5.4-mini --model-name gpt-5.4-mini --model-version 2026-03-17 --model-format OpenAI --sku-name GlobalStandard --sku-capacity 50
# if gpt-5.4-mini isn't offered, deploy a newer mini model and run: export BREZY_MODEL=<deployment name>; whether the attack lands depends on the model
az role assignment create --assignee-object-id $(az ad signed-in-user show --query id -o tsv) --assignee-principal-type User --role "Cognitive Services User" --scope $(az cognitiveservices account show -n $AI -g $RG --query id -o tsv)   # Entra ID sign-in, no keys; can take a few minutes to apply
export BREZY_AI_ENDPOINT=$(az cognitiveservices account show -n $AI -g $RG --query properties.endpoint -o tsv)
python agent.py T-1042            # no defenses
python agent.py T-1042 --defend   # scoped tools, approval, Prompt Shields
python agent.py T-1044 --defend   # a blunter injection that Prompt Shields flags
```

Model output differs from run to run. Tokens and Prompt Shields calls are billed per use; nothing here has an hourly charge.

## Tear down

```bash
az group delete -n rg-brezyweather-support-agent --yes
az cognitiveservices account list-deleted -o table   # a deleted account is kept, and its name reserved, until purged
az cognitiveservices account purge -l eastus2 -g rg-brezyweather-support-agent -n $AI   # set AI to the name in the list if this is a new terminal
```
