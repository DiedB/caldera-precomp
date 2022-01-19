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

            for port in host.findall("ports/port"):
                port_number = port.get("portid")
                port_state = port.find("state")

                # Check if port is open
                is_open = port_state.get("state") == "open"

                if is_open:
                    for mp in self.mappers:
                        source = self.set_value(mp.source, port_number, self.used_facts)
                        target = self.set_value(mp.target, address, self.used_facts)
                        relationships.append(
                            Relationship(
                                source=Fact(mp.source, source),
                                edge=mp.edge,
                                target=Fact(mp.target, target),
                            )
                        )

        return relationships
