# (Pre-)compromise operations for CALDERA

Extend your CALDERA operations over the entire adversary killchain. In contrast to MITRE's [access](https://github.com/mitre/access) plugin, `caldera-precomp` attempts to traverse the first phases of the killchain (reconnaissance, initial access, command and control) in an autonomous manner.

Even more so than post-compromise operation, the (pre-)compromise domain is full of uncertainty and subject to constant change. For this reason and a multitude of other reasons, the scenarios implemented in the plugin are unlikely to be very effective in the real world - they have mainly been built as a proof-of-concept. However, the underlying architecture of the plugin forms a great platform for autonomous (pre-)compromise operation. Use the plugin as a learning resource, or a basis for developing your own AAE applications that traverse the entire killchain.

## Usage

```
⚠️ Only use this against resources that you own and/or are authorised to attack
```

- The plugin needs a target scope to start with - see [fact sources](#fact-sources).
- The plugin has been built and tested against MITRE CALDERA `4.0.0-alpha`.
- The plugin assumes availability of tooling required to run abilities on `initial` agents - Docker and bundled payloads have been used where possible to limit setup complexity.

## Plugin architecture

### Agents and agent groups

- `initial` agents are used as a vantage point for the operation - they are installed on hosts that are controlled by us. We recommend spawning multiple on a range of OS'es and architectures - it can be useful to have both Windows and Linux-based agents to maximise support for tooling used by abilities.
- `rce` agents are used as a 'mask' for situations where remote code execution is possible. This is part of a workaround that is further documented [here](#handling-rce).
- `target` agents are spawned on remote hosts. This plugin does not interact with target agents, but they can be used to transition towards post-compromise adversary emulation using other CALDERA plugins.

### Adversaries

The plugin implements two types of adversaries - ones that follow predefined scenarios albeit in an autonomous manner, and one that works unrestricted and leverages all abilities the plugin implements.

#### Scenarios

- `precomp-scenario-vulnexp` scans the IP range for public-facing Microsoft Exchange servers and checks whether they are vulnerable to ProxyShell (CVE-2021-34473, CVE-2021-34523, and CVE-2021-31207). If it finds any vulnerable hosts, it exploits the vulnerability, extracting all email addresses from the Exchange Server and dropping a webshell. The webshell is then used to spawn a Sandcat agent on the remote Exchange server.
- `precomp-scenario-spray` scans public-facing websites for email addresses and the target IP range for public-facing RDP servers. The resulting information is used to execute a password spray against RDP. If successful, the adversary logs in to RDP and spawns a Sandcat agent on the remote host.
- `precomp-scenario-phish` scans public-facing websites for email addresses, generates a malicious Office document which - when macros are enabled - calls back to the CALDERA server which hosts a PowerShell dropper. On execution of this dropper, a Sandcat agent is spawned on the remote host. The email is based on a payload `.eml` file.

#### Autonomous

- `precomp-unrestricted` implements all abilities that are part of the plugin and thus traverses any path it can find within the boundaries of the plugin.

### Fact sources

This plugin needs two types of fact sources - `target` sources that define the scope of the operation, and `internal` sources that are necessary for configuring the plugin itself.

- `target.domain` takes a domain name (`example.com`)
- `target.range` takes an IP address or range of addresses in CIDR notation (`10.0.0.0/28`)

Most `internal` fact traits are necessary to execute phishing campaigns and are self-explanatory - see [the included sources file](data/sources/ac86e9e6-8e5e-42c6-ad24-a7aa4d16f350.yml) for their traits and example values.

### Planning

The included `precomp-planner` ensures three conditions apply for the links it generates:

- For agents in the `initial` group, a combination of an ability and facts is only executed by one of these agents (since initial agents are identical from a tactical perspective)
- RCE agents only execute abilities in the `command-and-control` tactic (in our scenarios, we want to 'upgrade' to full C2 as soon as possible)
- Target agents do not execute any abilities

While this behaviour is sufficient for our use case, it might not be for other scenarios. Modify the [planner](app/planners/planner.py) logic as you like.

### Handling RCE

When designing abilities that are part of the tactical phases of inital access or lateral movement, procedures often yield the ability to execute code on a target host (remote code execution). In these situations, actually executing code on the remote host requires two separate actions: one that is run locally, to establish the 'pipe' through which commands can be executed, and the action that is run remotely.

Given CALDERA's current capability, it is not possible to separate these two actions - both will have to be combined into one ability. Doing this goes directly against the philosophy of the framework - to strive for atomicity in designing abilities, while letting the framework make decisions in how to use them.

To solve this without modifying the CALDERA framework itself, we forked and modified MITRE's [Sandcat agent](https://github.com/mitre/gocat) to essentially act as a 'mask' for remote code execution - it runs locally, but acts like a remote agent and ensures any commands sent to it are executed on the remote host. This 'workaround' can be used as an intermediate stage to gaining full C2 (by installing an agent on the remote host).

An example of this agent being used in an ability can be found [here](data/abilities/initial-access/554cc237-02c1-423f-ba52-e612bd1b4d1c.yml). The modified agent can be found [here](https://github.com/DiedB/caldera-precomp-gocat-rce). Compiled versions of this agent (for Linux and Windows) can be found in the payloads of this plugin.

### Arguments

- `rcePlatform`: the platform of the remote host (e.g. `windows`, `darwin`).
- `rceExecutor`: the executor to use for remotely executed commands (e.g. `psh`, `sh`).
- `rceCommand`: the command to use to 'instantiate' RCE (e.g. `ssh root@remote-host COMMAND`). This command needs to include a substitution marker (`COMMAND`), allowing the RCE agent to inject actions that need to be executed on the remote system.
- `rcePayloadname`: if necessary, the payload to download from the CALDERA server that is a prerequisite to executing the `rceCommand`.
