# Requirements

## Introduction

The `nebius-client` feature provides a REST client for Nebius, exposing
project enumeration, networking (VPC/subnet/security-group),
SSH keys, images, instance lifecycle, disks, IB-enabled placement
groups, and native shared filesystems. Transport is REST on
`RestClientBase`. Authentication uses `NebiusServiceAccountCredential`.
Every behaviour-bearing method accepts
`aspects: AspectsRest = DEFAULT_NEBIUS_ASPECTS`.

---

## Requirements

### Requirement 1: Authenticate

#### Acceptance Criteria

1. WHEN the client is constructed with a `NebiusServiceAccountCredential`
   THE SYSTEM SHALL exchange the service-account JWT for an access token
   and configure `RestClientBase` to inject it on every call.
2. WHEN the credential is missing required fields THE SYSTEM SHALL raise
   `ConfigurationError`.
3. WHEN HTTP 401/403 is returned THE SYSTEM SHALL reclassify into
   `NebiusAuthenticationError`.
4. WHEN the access token nears expiry THE SYSTEM SHALL re-mint it
   transparently without surfacing the renewal to the caller.

### Requirement 2: Enumerate Projects, Regions, and Image Catalog

#### Acceptance Criteria

1. WHEN the caller invokes `list_projects(aspects)` THE SYSTEM SHALL
   return `NebiusProject` records.
2. WHEN the caller invokes `list_regions(aspects)` THE SYSTEM SHALL
   return `NebiusRegion` records.
3. WHEN the caller invokes `list_images(aspects)` THE SYSTEM SHALL
   return `NebiusImage` records with name, family, version, architecture.

### Requirement 3: Manage VPCs and Subnets

#### Acceptance Criteria

1. WHEN the caller invokes `create_vpc(spec, aspects)` THE SYSTEM SHALL
   return a `NebiusVpc` record; an existing VPC of the same name in the
   same project SHALL be returned (idempotent create).
2. WHEN the caller invokes `create_subnet(spec, aspects)` and the subnet
   CIDR is not contained in the VPC CIDR THE SYSTEM SHALL raise
   `NebiusCidrValidationError`.
3. WHEN the caller invokes `list_vpcs(project_id, aspects)` and
   `list_subnets(vpc_id, aspects)` THE SYSTEM SHALL follow paging cursors.
4. WHEN `delete_*` is called against an unknown id THE SYSTEM SHALL
   succeed as a no-op.

### Requirement 4: Manage Security Groups

#### Acceptance Criteria

1. WHEN the caller invokes `create_security_group(spec, aspects)` and
   `set_security_group_rules(sg_id, ingress, egress, aspects)` THE SYSTEM
   SHALL POST the requests and return typed records.
2. Idempotent create-by-name; idempotent delete on unknown id.

### Requirement 5: Manage SSH Keys

#### Acceptance Criteria

1. WHEN the caller invokes `register_ssh_key(name, public_key, aspects)`
   THE SYSTEM SHALL register the key idempotently.
2. WHEN `delete_ssh_key(key_id, aspects)` is called against an unknown
   id THE SYSTEM SHALL succeed as a no-op.

### Requirement 6: Manage Disks

#### Acceptance Criteria

1. WHEN the caller invokes `create_disk(spec, aspects)` THE SYSTEM SHALL
   return a `NebiusDisk` and a `NebiusTaskHandle`.
2. WHEN the caller invokes `attach_disk(disk_id, instance_id, aspects)`
   or `detach_disk(disk_id, instance_id, aspects)` THE SYSTEM SHALL return
   a `NebiusTaskHandle`.
3. Idempotent delete on unknown id.

### Requirement 7: Manage IB-Enabled Placement Groups

#### Acceptance Criteria

1. WHEN the caller invokes `create_placement_group(spec, aspects)` with
   `interconnect="infiniband"` THE SYSTEM SHALL return a `NebiusPlacementGroup`.
2. Idempotent create-by-name; idempotent delete.

### Requirement 8: Launch and Manage Virtual Machines

#### Acceptance Criteria

1. WHEN the caller invokes `launch_vm(spec, aspects)` THE SYSTEM SHALL
   POST and return both a `NebiusVm` record and a `NebiusTaskHandle`.
2. WHEN the spec's GPU SKU is unavailable in the chosen region THE SYSTEM
   SHALL raise `NebiusAcceleratorNotAvailableError` before issuing the
   request.
3. WHEN the caller invokes `get_vm`, `list_vms`, `power_on_vm`,
   `power_off_vm`, or `terminate_vm` THE SYSTEM SHALL behave per HTTP
   semantics with idempotent terminate.

### Requirement 9: Manage Native Shared Filesystems

#### Acceptance Criteria

1. WHEN the caller invokes `create_filesystem(spec, aspects)` THE SYSTEM
   SHALL POST and return a `NebiusFilesystem` record + `NebiusTaskHandle`.
2. WHEN the caller invokes `create_mount_target(spec, aspects)` THE SYSTEM
   SHALL attach the filesystem to a subnet and return a `NebiusMountTarget`.
3. Idempotent create-by-name; idempotent delete on unknown id.

### Requirement 10: Tagging

#### Acceptance Criteria

1. WHEN the caller invokes `apply_tags(resource_type, resource_id, tags, aspects)`
   THE SYSTEM SHALL PATCH the resource with the supplied tag set, translating
   from the neutral `List[Dict[str, str]]` shape.

### Requirement 11: Long-Running Task Handles

#### Acceptance Criteria

1. THE SYSTEM SHALL return `NebiusTaskHandle` (implementing `ITaskHandle`)
   for all async operations.
2. `handle.wait(aspects)` polls per aspects and raises `TimeoutError`
   on budget exhaustion.

### Requirement 12: URL Composition

#### Acceptance Criteria

1. Per-segment percent-encoding; empty/`None` identifier raises
   `SemanticError`.

### Requirement 13: Aspects on Every Behaviour-Bearing Call

#### Acceptance Criteria

1. THE SYSTEM SHALL accept `aspects: AspectsRest = DEFAULT_NEBIUS_ASPECTS`
   on every I/O method; no behaviour-modifying decorators.
