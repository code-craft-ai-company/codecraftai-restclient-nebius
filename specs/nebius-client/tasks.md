# Implementation Plan — Nebius Client

## Package Skeleton

- [x] 1. Create `source/packages/ccai/restclient/nebius/` package tree.
- [x] 2. Add `aspectsnebius.py` with `DEFAULT_NEBIUS_ASPECTS`.

## Client Core

- [x] 3. Implement `NebiusClient(RestClientBase)` with service-account JWT exchange and transparent token refresh.
- [x] 4. Implement URL composition helper.
- [x] 5. Implement HTTP-error reclassification.

## Data Model & Specs

- [x] 6. Implement model dataclasses for projects, regions, images, VPCs, subnets, security groups, SSH keys, disks, placement groups, VMs, filesystems, mount targets, operations.
- [x] 7. Implement corresponding spec dataclasses.
- [x] 8. Implement `NebiusTaskHandle` against `ITaskHandle`.

## API Groups

- [x] 9. Implement `ProjectsGroup`, `RegionsGroup`, `ImagesGroup` enumeration calls.
- [x] 10. Implement `VpcsGroup` and `SubnetsGroup` (idempotent + CIDR validation).
- [x] 11. Implement `SecurityGroupsGroup`.
- [x] 12. Implement `SshKeysGroup`.
- [x] 13. Implement `DisksGroup` with task-handle returns.
- [x] 14. Implement `PlacementGroupsGroup` with IB support.
- [x] 15. Implement `VmsGroup` with accelerator-availability validation.
- [x] 16. Implement `FilesystemsGroup` and `MountTargetsGroup`.
- [x] 17. Implement `TagsGroup.apply`.
- [x] 18. Implement `OperationsGroup.get`.

## Paging

- [x] 19. Transparent cursor traversal in every `list_*`.

## Tests — Example-Based

- [x] 20. Authentication + token-refresh tests.
- [x] 21. Idempotent create tests across resource families.
- [x] 22. VM launch + filesystem mount happy paths.
- [x] 23. HTTP-error reclassification.

## Tests — Property-Based (hypothesis)

- [x] 24. Paging traversal totality.
- [x] 25. URL composition determinism + encoding + rejection.
- [x] 26. Idempotent-retry equivalence.
- [x] 27. CIDR containment correctness.
- [x] 28. `NebiusTaskHandle.wait` terminal-state correctness.

## Integration

- [x] 29. Smoke-test fixture for live Nebius API.
