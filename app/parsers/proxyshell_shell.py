import json
import re

from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.utility.base_parser import BaseParser


regex = re.compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+")


class Parser(BaseParser):
    def parse(self, blob):
        relationships = []

        # Output should be a JSON array
        data = json.loads(blob)

        if data['url']:
            for mp in self.mappers:
                source = self.set_value(mp.source, data['url'], self.used_facts)
                target = self.set_value(mp.target, data['url'], self.used_facts)
                relationships.append(
                    Relationship(
                        source=Fact(mp.source, source),
                        edge=mp.edge,
                        target=Fact(mp.target, target),
                    )
                )
        return relationships

    @staticmethod
    def _is_valid_email(email):
        return bool(re.fullmatch(regex, email))
