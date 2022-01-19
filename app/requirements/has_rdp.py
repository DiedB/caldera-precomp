class Requirement:
    def __init__(self, requirement_info):
        self.enforcements = requirement_info["enforcements"]

    # Checks for presence of an RDP service from the output of an Nmap scan
    async def enforce(self, link, operation):
        relationships = await operation.all_relationships()

        for uf in link.used:
            if self.enforcements["target"] == uf.trait:

                # Naive check for now - can be made more rigid by checking the service fingerprint
                return "3389" in [
                    r.source.value for r in relationships if r.target.value == uf.value
                ]

        return False
