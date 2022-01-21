from aiohttp import web
import os
from urllib.parse import unquote, urlparse


PAYLOAD_DIR = os.path.realpath("plugins/precomp/data/payloads/")
AGENT_DROPPER_ABILITY = "38b639c7-4812-4933-9356-c1877d1eec03"


class PrecompAPI:
    def __init__(self, services):
        self.services = services
        self.auth_svc = self.services.get("auth_svc")
        self.data_svc = self.services.get("data_svc")

    # Serves a PSH Sandcat agent dropper (by getting the command from the respective ability)
    async def get_agent_dropper(self, request):

        abilities = await self.data_svc.locate(
            "abilities", match=dict(ability_id=AGENT_DROPPER_ABILITY)
        )

        if len(abilities):
            psh_agent = next(
                a for a in abilities[0].display["executors"] if a["name"] == "psh"
            )

            request_url_parse = urlparse(str(request.url))
            request_url = f"{request_url_parse.scheme}://{request_url_parse.netloc}"

            if psh_agent:
                return web.Response(
                    body=psh_agent["command"].replace(
                        "#{app.contact.http}", request_url
                    ),
                    headers={
                        "Content-Type": "text/plain",
                    },
                )

        return web.HTTPNotFound(body="Dropper not found")
