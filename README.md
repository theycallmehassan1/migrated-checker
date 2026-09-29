# Legacy Endpoint Reachability Checker

A small command-line utility for the discovery phase of a legacy-to-cloud
or zero-trust transition. Given a CSV inventory of hosts and ports, it
checks which are currently reachable over TCP and reports the connection
latency, or the error, for each one.

This is the kind of check that belongs in the environment intake step
before any scoring or planning happens, confirming what actually answers
on the network rather than relying on documentation that may be years out
of date. It complements the Workload Register sheet in the
[Transition-State Zero Trust Adoption Toolkit](https://github.com/theycallmehassan1/transition-state-zero-trust-toolkit).

## What it does, and does not do

- Opens a single TCP connection to each host:port pair in the inventory
  and records whether it succeeded, and how long it took.
- Sends no credentials, no payloads, and performs no port scanning beyond
  the one port listed for each row.
- Writes a plain CSV of results if you ask for one.

It is intentionally simple. It answers one question: "is this thing
listening," nothing more.

## Usage

```bash
pip install -r requirements.txt   # no third-party dependencies; stdlib only
python3 reachability_checker.py inventory.csv
python3 reachability_checker.py inventory.csv --timeout 5 --out results.csv
```

`inventory.csv` needs a header row with `name,host,port`:

```csv
name,host,port
file-server,fs01.internal.example,445
tax-software-db,db01.internal.example,1433
m365-admin,outlook.office365.com,443
```

A working sample is included at [`sample_inventory.csv`](sample_inventory.csv),
checking a public DNS-over-HTTPS endpoint (reachable) and a documentation-only
IP address from RFC 5737 (deliberately unreachable), so the script can be
tried immediately without pointing it at anything internal:

```bash
python3 reachability_checker.py sample_inventory.csv
```

## Testing

```bash
python3 -m unittest test_reachability_checker.py -v
```

## License

Released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
consistent with the toolkit this complements. Use it, adapt it.
