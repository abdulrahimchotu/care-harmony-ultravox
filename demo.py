from fastapi import FastAPI,Request
import uvicorn
import os
import json
import aiohttp
import asyncio
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect


load_dotenv()

app = FastAPI()

# Environment variables
agent_id = os.environ['ULTRAVOX_AGENT_ID2']
api_key = os.environ['ULTRAVOX_API_KEY2']
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']

print(account_sid,auth_token)
# Twilio client
client = Client(account_sid, auth_token)

# API URL and payload
ultravox_url = f"https://api.ultravox.ai/api/agents/{agent_id}/calls"
payload = {
    "templateContext": {
        "agentName" : "Care Harmony",
        "referringProviderName" : "Smith",
        "patientFullName" : "Johnson",
        "patientFirstName" : "Mitchell",
        "patientDOB" : "14th April 1980",
        "clinicName" : "ABC"

    },
    "medium": {
        "twilio": {}
    }
}

@app.get("/get-url/{number}")
async def get_url(number:int):
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(ultravox_url, headers=headers, json=payload) as response:
            if response.status != 201:
                return {"error": f"Ultravox returned status {response.status}", "details": await response.text()}

            try:
                data = await response.json()
            except Exception:
                return {"error": "Invalid JSON response from Ultravox", "raw_response": await response.text()}

    join_url = data.get("joinUrl")
    print(join_url)
    if not join_url:
        return {"error": "No joinUrl found in response."}

    call_response = await make_call(join_url,number)
    return {
        "message": "Got joinUrl, making call...",
        "call": call_response
    }

async def make_call(join_url,to_num):
    try:
        # TwiML creation
        response = VoiceResponse()
        connect = Connect()
        connect.stream(url=join_url)
        response.append(connect)

        call=client.calls.create(twiml=str(response),to=to_num,from_="+18889585233")
        return {"message": "Call made!", "call_sid": call.sid}

    except Exception as e:
        return {"error": str(e)}
    



if __name__ == "__main__":
    uvicorn.run("demo:app", port=8000, reload=True)