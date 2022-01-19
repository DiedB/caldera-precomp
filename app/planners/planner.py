from time import sleep

# Agent groups
RCE_AGENT_GROUP = "rce"
INITIAL_AGENT_GROUP = "initial"

# Global stores
operation_ids = []
execution_memory = set()


class LogicalPlanner:
    def __init__(self, operation, planning_svc, stopping_conditions=()):
        self.operation = operation
        self.planning_svc = planning_svc
        self.stopping_conditions = stopping_conditions
        self.stopping_condition_met = False
        self.state_machine = ["precomp"]
        self.next_bucket = "precomp"

    async def execute(self):
        # Keep list of operations the planner has been instantiated for (prevents CALDERA
        # bug where multiple planners are instantiated for the same operation)
        if self.operation.id not in operation_ids:
            operation_ids.append(self.operation.id)
            await self.planning_svc.execute_planner(self)

    # Default bucket, runs all abilities that are satisfied in terms of knowledge
    # Constrains C2 abilities to RCE agents
    async def precomp(self):
        links = await self._get_filtered_links()

        while links:
            link_ids = [await self.operation.apply(link) for link in links]
            await self.operation.wait_for_links_completion(link_ids)

            # Fetch new links
            links = await self._get_filtered_links()

            # Wait a bit before trying new links
            sleep(0.5)

    # Reduces set of links
    async def _get_filtered_links(self):

        # Combine precomp abilities with initial agents, c2 abilities with RCE agents
        initial_links = []
        for agent in self._get_agents(INITIAL_AGENT_GROUP):
            for link in await self._get_links(agent):
                link_hash = self._hash_link(link)

                # Deduplication: prevent the same combination of an ability and facts to
                # be used from multiple initial agents, by storing a hash of a serialized
                # representation of the combination into an execution memory
                if (
                    link.ability.tactic != "command-and-control"
                    and link_hash not in execution_memory
                ):
                    execution_memory.add(link_hash)
                    initial_links.append(link)

        return initial_links + [
            link
            for agent in self._get_agents(RCE_AGENT_GROUP)
            for link in await self._get_links(agent)
            if link.ability.tactic == "command-and-control"
        ]

    # Returns a list of agents in this operation, filtered by their group
    def _get_agents(self, group):
        return [agent for agent in self.operation.agents if agent.group == group]

    # Returns a unique hash for a link
    def _hash_link(self, link):
        # Serialize this combination of ability and its facts
        used_facts = ";".join(sorted([f"{f.trait},{f.value}" for f in link.used]))

        return hash(f"{link.ability.ability_id}:{used_facts}")

    async def _get_links(self, agent=None):
        return await self.planning_svc.get_links(operation=self.operation, agent=agent)
