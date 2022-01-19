import json

from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.utility.base_parser import BaseParser


class Parser(BaseParser):
    def parse(self, blob):
        relationships = []

        hydra_output = json.loads(blob)

        # Store credential

        # TODO: link credential to service
        for result in hydra_output["results"]:
            for mp in self.mappers:
                source = self.set_value(mp.source, result["password"], self.used_facts)
                target = self.set_value(mp.target, result["login"], self.used_facts)
                relationships.append(
                    Relationship(
                        source=Fact(mp.source, source),
                        edge=mp.edge,
                        target=Fact(mp.target, target),
                    )
                )

        return relationships
