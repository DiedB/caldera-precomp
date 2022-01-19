import json
import re

from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.utility.base_parser import BaseParser


regex = re.compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+")


class Parser(BaseParser):
    def parse(self, blob):
        relationships = []

        # Spiderfoot output should be a JSON array
        data = json.loads(blob)

        for spf_result in data:
            email = spf_result["data"]
            if self._is_valid_email(email):
                for mp in self.mappers:
                    source = self.set_value(mp.source, email, self.used_facts)
                    target = self.set_value(mp.target, email, self.used_facts)
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
