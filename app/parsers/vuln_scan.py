import xml.etree.ElementTree as ET

from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.utility.base_parser import BaseParser


class Parser(BaseParser):
    def parse(self, blob):
        relationships = []

        root = ET.fromstring(blob)

        for host in root.findall("host"):

            # Get the IP address of the current target
            address = host.find("address").get("addr")

            # Enumerate scripts that were executed in this scan
            for script in host.findall("ports/port/script"):

                # Get the script id and check vulnerability
                vuln_id = script.get("id")
                is_vulnerable = script.get("output") == "True"

                if is_vulnerable:
                    for mp in self.mappers:
                        source = self.set_value(mp.source, vuln_id, self.used_facts)
                        target = self.set_value(mp.target, address, self.used_facts)
                        relationships.append(
                            Relationship(
                                source=Fact(mp.source, source),
                                edge=mp.edge,
                                target=Fact(mp.target, target),
                            )
                        )

        return relationships
