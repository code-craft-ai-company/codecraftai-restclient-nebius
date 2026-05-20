"""
    .. module:: test_apigroups
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Tests for Nebius api-group methods — idempotent create,
                   CIDR validation, VM launch, filesystem + mount-target
                   lifecycle, and idempotent delete.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import pytest
import requests_mock as rm_module

from automojo.interop.nebius.exceptions.nebiusexceptions import (
    NebiusAcceleratorNotAvailableError, NebiusCidrValidationError
)
from automojo.interop.nebius.specs.nebiusvpcspec import NebiusVpcSpec
from automojo.interop.nebius.specs.nebiussubnetspec import NebiusSubnetSpec
from automojo.interop.nebius.specs.nebiussecuritygroupspec import (
    NebiusSecurityGroupSpec
)
from automojo.interop.nebius.specs.nebiusdiskspec import NebiusDiskSpec
from automojo.interop.nebius.specs.nebiusplacementgroupspec import (
    NebiusPlacementGroupSpec
)
from automojo.interop.nebius.specs.nebiusvmspec import NebiusVmSpec
from automojo.interop.nebius.specs.nebiusfilesystemspec import (
    NebiusFilesystemSpec
)
from automojo.interop.nebius.specs.nebiusmounttargetspec import (
    NebiusMountTargetSpec
)

from automojo.tests.interop.nebius.testsupport import (
    TEST_BASE, make_client, register_token_exchange
)


def test_list_projects_follows_paging_cursor():
    """
        ``projects.list`` walks every page following the cursor.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        responses = [
            {"json": {"items": [{"id": "p1"}],
                      "next_page_token": "tok2"}},
            {"json": {"items": [{"id": "p2"}]}},
        ]
        mock.get("{}/v1/projects".format(TEST_BASE), responses)

        projects = client.projects.list()

    ids = [p.id for p in projects]
    assert ids == ["p1", "p2"]
    return


def test_create_vpc_is_idempotent_by_name():
    """
        ``vpcs.create`` returns an existing VPC of the same name without
        issuing a POST.
    """
    client = make_client()
    spec = NebiusVpcSpec(parent_id="proj-1", name="vpc-a",
                         ipv4_cidr_block="10.0.0.0/16")
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/vpcs".format(TEST_BASE),
                 json={"items": [{"id": "vpc-existing", "name": "vpc-a",
                                  "ipv4_cidr_block": "10.0.0.0/16"}]})
        post_marker = mock.post("{}/v1/vpcs".format(TEST_BASE),
                                json={"id": "should-not-be-used"})

        vpc = client.vpcs.create(spec=spec)

        assert post_marker.called is False
    assert vpc.id == "vpc-existing"
    return


def test_create_vpc_posts_when_absent():
    """
        ``vpcs.create`` POSTs when no VPC of the name exists.
    """
    client = make_client()
    spec = NebiusVpcSpec(parent_id="proj-1", name="vpc-new",
                         ipv4_cidr_block="10.1.0.0/16")
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/vpcs".format(TEST_BASE), json={"items": []})
        mock.post("{}/v1/vpcs".format(TEST_BASE),
                  json={"id": "vpc-new-id", "name": "vpc-new",
                        "ipv4_cidr_block": "10.1.0.0/16"})

        vpc = client.vpcs.create(spec=spec)

    assert vpc.id == "vpc-new-id"
    return


def test_create_subnet_rejects_uncontained_cidr():
    """
        ``subnets.create`` raises when the subnet CIDR is not contained in
        the VPC CIDR.
    """
    client = make_client()
    spec = NebiusSubnetSpec(vpc_id="vpc-1", name="sub-a",
                            ipv4_cidr_block="192.168.1.0/24",
                            zone_id="zone-a")
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/vpcs/vpc-1".format(TEST_BASE),
                 json={"id": "vpc-1", "ipv4_cidr_block": "10.0.0.0/16"})

        with pytest.raises(NebiusCidrValidationError):
            client.subnets.create(spec=spec)
    return


def test_create_subnet_accepts_contained_cidr():
    """
        ``subnets.create`` succeeds when the subnet CIDR is contained.
    """
    client = make_client()
    spec = NebiusSubnetSpec(vpc_id="vpc-1", name="sub-a",
                            ipv4_cidr_block="10.0.1.0/24",
                            zone_id="zone-a")
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/vpcs/vpc-1".format(TEST_BASE),
                 json={"id": "vpc-1", "ipv4_cidr_block": "10.0.0.0/16"})
        mock.get("{}/v1/subnets".format(TEST_BASE), json={"items": []})
        mock.post("{}/v1/subnets".format(TEST_BASE),
                  json={"id": "sub-id", "name": "sub-a"})

        subnet = client.subnets.create(spec=spec)

    assert subnet.id == "sub-id"
    return


def test_create_security_group_idempotent():
    """
        ``security_groups.create`` is idempotent by name within a VPC.
    """
    client = make_client()
    spec = NebiusSecurityGroupSpec(vpc_id="vpc-1", name="sg-a")
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/security-groups".format(TEST_BASE),
                 json={"items": [{"id": "sg-existing", "name": "sg-a"}]})
        post_marker = mock.post("{}/v1/security-groups".format(TEST_BASE),
                                json={"id": "x"})

        sg = client.security_groups.create(spec=spec)
        assert post_marker.called is False
    assert sg.id == "sg-existing"
    return


def test_register_ssh_key_idempotent():
    """
        ``ssh_keys.register`` returns an existing key of the same name.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/ssh-keys".format(TEST_BASE),
                 json={"items": [{"id": "key-1", "name": "kp-a"}]})
        post_marker = mock.post("{}/v1/ssh-keys".format(TEST_BASE),
                                json={"id": "x"})

        key = client.ssh_keys.register(name="kp-a", public_key="ssh-rsa AAA")
        assert post_marker.called is False
    assert key.id == "key-1"
    return


def test_delete_unknown_id_is_no_op():
    """
        A delete against a 404 succeeds as a no-op for every family.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.delete("{}/v1/vpcs/missing".format(TEST_BASE), status_code=404)
        mock.delete("{}/v1/disks/missing".format(TEST_BASE), status_code=404)
        mock.delete("{}/v1/ssh-keys/missing".format(TEST_BASE),
                    status_code=404)

        client.vpcs.delete(vpc_id="missing")
        client.disks.delete(disk_id="missing")
        client.ssh_keys.delete(key_id="missing")
    return


def test_create_disk_returns_task_handle():
    """
        ``disks.create`` returns a typed model plus a task handle.
    """
    client = make_client()
    spec = NebiusDiskSpec(parent_id="proj-1", name="disk-a",
                          size_bytes=10_000_000_000, type="ssd")
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.post("{}/v1/disks".format(TEST_BASE),
                  json={"resource": {"id": "disk-id", "name": "disk-a"},
                        "operation_id": "op-disk-1"})

        disk, handle = client.disks.create(spec=spec)

    assert disk.id == "disk-id"
    assert handle.operation_id == "op-disk-1"
    return


def test_create_placement_group_with_infiniband():
    """
        ``placement_groups.create`` carries the infiniband interconnect.
    """
    client = make_client()
    spec = NebiusPlacementGroupSpec(parent_id="proj-1", name="pg-a",
                                    interconnect="infiniband")
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/placement-groups".format(TEST_BASE),
                 json={"items": []})
        mock.post("{}/v1/placement-groups".format(TEST_BASE),
                  json={"id": "pg-id", "name": "pg-a",
                        "interconnect": "infiniband"})

        pg = client.placement_groups.create(spec=spec)

    assert pg.id == "pg-id"
    assert pg.interconnect == "infiniband"
    return


def test_launch_vm_returns_model_and_handle():
    """
        ``vms.launch`` POSTs and returns both a record and a task handle.
    """
    client = make_client()
    spec = NebiusVmSpec(parent_id="proj-1", name="vm-a",
                        platform="gpu-h100-sxm", preset="8gpu-128vcpu",
                        subnet_id="sub-1", image_id="img-1")
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.post("{}/v1/instances".format(TEST_BASE),
                  json={"resource": {"id": "vm-id", "name": "vm-a"},
                        "operation_id": "op-vm-1"})

        vm, handle = client.vms.launch(spec=spec)

    assert vm.id == "vm-id"
    assert handle.operation_id == "op-vm-1"
    return


def test_launch_vm_rejects_unavailable_gpu_platform():
    """
        ``vms.launch`` raises before POSTing when the GPU platform is not
        available in the chosen region.
    """
    client = make_client()
    spec = NebiusVmSpec(parent_id="proj-1", name="vm-a",
                        platform="gpu-h200-nvl", preset="8gpu",
                        subnet_id="sub-1", image_id="img-1",
                        region_id="eu-north1")
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/platforms".format(TEST_BASE),
                 json={"items": [{"id": "gpu-h100-sxm"}]})
        post_marker = mock.post("{}/v1/instances".format(TEST_BASE),
                                json={"id": "x"})

        with pytest.raises(NebiusAcceleratorNotAvailableError):
            client.vms.launch(spec=spec)
        assert post_marker.called is False
    return


def test_terminate_vm_idempotent_on_404():
    """
        ``vms.terminate`` returns None when the VM is already absent.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.delete("{}/v1/instances/gone".format(TEST_BASE),
                    status_code=404)

        handle = client.vms.terminate(vm_id="gone")

    assert handle is None
    return


def test_filesystem_and_mount_target_lifecycle():
    """
        Create a shared filesystem then a mount target attaching it to a
        subnet.
    """
    client = make_client()
    fs_spec = NebiusFilesystemSpec(parent_id="proj-1", name="fs-a",
                                   size_bytes=50_000_000_000_000)
    mt_spec = NebiusMountTargetSpec(filesystem_id="fs-id",
                                    subnet_id="sub-1", mount_path="/shared")
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/file-storages".format(TEST_BASE),
                 json={"items": []})
        mock.post("{}/v1/file-storages".format(TEST_BASE),
                  json={"resource": {"id": "fs-id", "name": "fs-a"},
                        "operation_id": "op-fs-1"})
        mock.get("{}/v1/mount-targets".format(TEST_BASE),
                 json={"items": []})
        mock.post("{}/v1/mount-targets".format(TEST_BASE),
                  json={"id": "mt-id", "filesystem_id": "fs-id",
                        "subnet_id": "sub-1"})

        fs, fs_handle = client.filesystems.create(spec=fs_spec)
        mount_target = client.mount_targets.create(spec=mt_spec)

    assert fs.id == "fs-id"
    assert fs_handle.operation_id == "op-fs-1"
    assert mount_target.id == "mt-id"
    return


def test_apply_tags_translates_neutral_shape():
    """
        ``tags.apply`` translates the neutral tag shape into a labels dict
        and PATCHes the resource.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        patch_marker = mock.patch("{}/v1/vpcs/vpc-1".format(TEST_BASE),
                                  json={"id": "vpc-1"})

        client.tags.apply(resource_type="vpc", resource_id="vpc-1",
                          tags=[{"env": "ci"}, {"team": "infra"}])

        body = patch_marker.last_request.json()
        assert body["labels"] == {"env": "ci", "team": "infra"}
    return
