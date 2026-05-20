# Design

## Overview

`NebiusClient` is a `RestClientBase` subclass that talks to Nebius'
REST control plane. Service-account JWT exchange yields a short-lived
access token; the client transparently refreshes it. The API surface
covers conventional IaaS primitives plus native shared filesystems and
IB-enabled placement groups.

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│  automojo-provisioning / venues / nebius               │
└──────────┬─────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│  NebiusClient                                          │
│   RestClientBase + AspectsRest                         │
│   API groups: projects, regions, images, vpcs,         │
│     subnets, security-groups, ssh-keys, disks,         │
│     placement-groups, vms, filesystems, mount-targets, │
│     tags, operations                                   │
└──────────┬─────────────────────────────────────────────┘
           │ HTTPS, JWT-exchanged bearer
           ▼
┌────────────────────────────────────────────────────────┐
│  api.nebius.cloud                                      │
└────────────────────────────────────────────────────────┘
```

---

## Data Model

`model/`: `nebiusproject.py`, `nebiusregion.py`, `nebiusimage.py`,
`nebiusvpc.py`, `nebiussubnet.py`, `nebiussecuritygroup.py`,
`nebiussshkey.py`, `nebiusdisk.py`, `nebiusplacementgroup.py`,
`nebiusvm.py`, `nebiusfilesystem.py`, `nebiusmounttarget.py`,
`nebiusoperationresult.py`, `nebiustaskhandle.py`.

`specs/`: matching `*spec.py` request payloads.

Exceptions: `NebiusAuthenticationError`, `NebiusCidrValidationError`,
`NebiusAcceleratorNotAvailableError`.

---

## Module Layout

```
source/packages/automojo/interop/nebius/
├── nebiusclient.py
├── aspectsnebius.py
├── apigroups/
├── model/
├── specs/
└── exceptions/
```

---

## See Also

- `automojo-restclient-base/specs/restapigroup-enhancements/`
- `automojo-provisioning/specs/venue-nebius/`
- `automojo-credentials/specs/nebius-credentials/`

---

## Testing Strategy

Example-based tests cover JWT exchange, token refresh on expiry,
idempotent create patterns, VM launch happy path, filesystem +
mount-target lifecycle, and HTTP-error reclassification.

Property-based tests (hypothesis) are **required** for:
1. **Paging cursor traversal** across all `list_*` endpoints.
2. **URL composition** — per-segment encoding, empty/`None` rejection.
3. **Idempotent retry semantics** within and beyond budget.
4. **CIDR containment** between VPC and subnet.
5. **`NebiusTaskHandle.wait`** terminal-state correctness against arbitrary
   monotonic mock status streams.
