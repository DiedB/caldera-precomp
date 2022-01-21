from app.utility.base_world import BaseWorld
from plugins.precomp.app.precomp_gui import PrecompGUI
from plugins.precomp.app.precomp_api import PrecompAPI

name = "Precomp"
description = "Pre-compromise procedures for CALDERA"
address = "/plugin/precomp/gui"
access = BaseWorld.Access.RED


async def enable(services):
    app = services.get("app_svc").application
    precomp_gui = PrecompGUI(services, name=name, description=description)
    app.router.add_static("/precomp", "plugins/precomp/static/", append_version=True)
    app.router.add_route("GET", "/plugin/precomp/gui", precomp_gui.splash)

    precomp_api = PrecompAPI(services)

    # Add API routes here
    app.router.add_route(
        "GET", "/plugin/precomp/dropper", precomp_api.get_agent_dropper
    )
