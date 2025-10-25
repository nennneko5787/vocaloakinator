import os
from typing import Dict, Literal

import aiohttp
import discord
import dotenv
import httpx
from fastapi import APIRouter, Form, Request
from fastapi.responses import PlainTextResponse

from services.ips import isFromCloudflare

dotenv.load_dotenv()

router = APIRouter()

webhook = discord.Webhook.from_url(
    os.getenv("webhook"), session=aiohttp.ClientSession()
)


@router.post("/api/contact")
async def contact(
    request: Request,
    name: str = Form(None),
    contactType: Literal["bug", "song", "other"] = Form(None),
    bugContent: str = Form(None),
    vocaloURL: str = Form(None),
    content: str = Form(None),
    agree: bool = Form(None),
    cfToken: str = Form(None, alias="cf-turnstile-response"),
):
    ipAddress = (
        request.headers.get["CF-Connecting-IP"]
        if isFromCloudflare(request.client.host)
        else request.client.host
    )

    if not name:
        name = "名無し"

    if not agree:
        return PlainTextResponse(
            "お問い合わせをするためには、注意事項に同意する必要があります。", 400
        )

    async with httpx.AsyncClient() as http:
        try:
            response = await http.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                json={
                    "secret": os.getenv("tsSecret"),
                    "response": cfToken,
                },
                timeout=10,
            )

            jsonData: Dict[str, str] = response.json()

            if not jsonData.get("success", False):
                return PlainTextResponse("spamお疲れ様！ｗ", 403)

        except httpx.RequestError as e:
            print(f"Turnstile validation error: {e}")
            return PlainTextResponse("spamお疲れ様！ｗ", 500)

        response = await http.get("https://www.vpngate.net/api/iphone/")
        if ipAddress in response.text:
            return PlainTextResponse("spamお疲れ様！ｗ", 500)

        response = await http.get(f"https://proxycheck.io/v3/{ipAddress}")
        jsonData: Dict[str, Dict[str, Dict[str, str]]] = response.json()

        detections = jsonData.get(ipAddress).get("detections")
        ayasii = False
        for key, value in detections.items():
            if key != "risk":
                if value:
                    ayasii = True

        if ayasii or detections["risk"] > 20:
            return PlainTextResponse("spamお疲れ様！ｗ", 500)

    if not contactType:
        return PlainTextResponse("spamお疲れ様！ｗ", 403)

    match contactType:
        case "bug":
            if not bugContent:
                return PlainTextResponse("spamお疲れ様！ｗ", 403)

            await webhook.send(
                embed=discord.Embed(
                    title="バグ報告",
                    description=discord.utils.escape_mentions(bugContent),
                )
                .set_author(name=name)
                .add_field(name="IPAddress", value=ipAddress),
            )
        case "song":
            if not vocaloURL:
                return PlainTextResponse("spamお疲れ様！ｗ", 403)

            await webhook.send(
                embed=discord.Embed(
                    title="ボカロ曲追加リクエスト",
                    description=discord.utils.escape_mentions(vocaloURL),
                )
                .set_author(name=name)
                .add_field(name="IPAddress", value=ipAddress),
            )
        case "other":
            if not content:
                return PlainTextResponse("spamお疲れ様！ｗ", 403)

            await webhook.send(
                embed=discord.Embed(
                    title="その他のお問い合わせ",
                    description=discord.utils.escape_mentions(content),
                )
                .set_author(name=name)
                .add_field(name="IPAddress", value=ipAddress),
            )

    return PlainTextResponse("お問い合わせは受理されました！ありがとうございます！")
