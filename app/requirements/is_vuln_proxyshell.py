class Requirement:
    def __init__(self, requirement_info):
        self.enforcements = requirement_info["enforcements"]

    # Checks for presence of the ProxyShell vulnerability from the output of an Nmap scan
    async def enforce(self, link, operation):
        relationships = await operation.all_relationships()

        for uf in link.used:
            if self.enforcements["target"] == uf.trait:

                return "exchange-proxyshell" in [
                    r.source.value for r in relationships if r.target.value == uf.value
                ]

        return False
