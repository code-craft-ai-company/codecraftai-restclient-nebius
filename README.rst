=========================================
Automation Mojo Interop - Nebius
=========================================

The ``automojo-interop-nebius`` package is the venue-specific REST client for Nebius, a
GPU-focused European cloud whose API exposes first-class InfiniBand-enabled placement
groups and a native shared-filesystem service suitable for distributed-training workloads.
Nebius shares enough of its shape with conventional IaaS providers to slot into the
neutral ``CloudProvisioner`` model defined in ``automojo-provisioning`` while adding the
GPU/RDMA dimensions covered by ``CloudAcceleratorSpec`` and ``CloudInterconnect``.

Highlights
==========

- ``NebiusClient`` — a ``RestClientBase`` subclass covering project enumeration, VPC/subnet/security-group lifecycle, SSH-key registration, and image lookup.
- Instance and storage lifecycle — instance launch/inspect/terminate, disk provisioning and attachment.
- Placement groups and shared filesystems — placement-group creation with interconnect kind, plus native shared-filesystem provisioning and mount-target management.
- Typed task handles — long-running operations return typed ``NebiusTaskHandle`` instances for the provisioner's verify stage.
- Aspects-driven transport — every behaviour-bearing call accepts ``aspects: AspectsRest = DEFAULT_NEBIUS_ASPECTS``; credentials enter as typed ``NebiusServiceAccountCredential`` instances from ``automojo-credentials``.

Repository Structure
====================

- ``development/`` - Runtime environment scripts.
- ``repository-setup/`` - Repository homing and setup scripts.
- ``source/packages/automojo/interop/nebius/`` - Package source code.
- ``source/testroots/testbase/automojo/tests/interop/nebius/`` - TestBase test roots.
- ``specs/`` - Requirements, design, and task documentation (Kiro-style).
- ``userguide/`` - Standards, conventions, and documentation.

Environment Setup
=================

When working in a Codex container:

.. code-block:: bash

   ./development/setup-agent-container

For local development:

.. code-block:: bash

   ./repository-setup/rehome-repository
   ./development/setup-environment

Running Tests
=============

.. code-block:: bash

   source .venv/bin/activate
   PYTHONPATH=source/packages:source/testroots/testbase python -m pytest source/testroots -q

Standards and Conventions
=========================

- Naming conventions: ``userguide/10-02-naming-conventions.rst``
- Code organization: ``userguide/10-01-code-organization.rst``
- Coding standards: ``userguide/10-00-coding-standards.rst``

Additional Resources
====================

- User guide entry point: ``userguide/userguide.rst``
