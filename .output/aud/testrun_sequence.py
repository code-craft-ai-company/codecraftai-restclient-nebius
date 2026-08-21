"""
    ======================================= CODE GENERATED - DO NOT EDIT =======================================
    This is a code generated execution sequence document, do not manually edit this document.  The 'testbase'
    test framework generates this document in order to layout the test run scopes, parameter creations, and
    test calls in a user ledgible way which is easy to read and also to debug.
"""

__traceback_format_policy__ = "Brief"

import logging

from ccai.xmodules.xlogging.enhancedloggers import getEnhancedLogger

from ccai.testbase.constraints import ConstraintsCatalog

logger = getEnhancedLogger()

constraints_catalog = ConstraintsCatalog()



def session(sequencer):
    """
    This is the entry point for the test run sequence document.
    """

    with sequencer.enter_session_scope_context() as ssc:


        scope_ccai(sequencer)

    return

def scope_ccai(sequencer):
    """
    This is the entry point for the 'ccai' test scope.
    """

    with sequencer.enter_module_scope_context("ccai") as msc:
        scope_ccai_tests(sequencer)

    return

def scope_ccai_tests(sequencer):
    """
    This is the entry point for the 'ccai_tests' test scope.
    """

    with sequencer.enter_module_scope_context("ccai.tests") as msc:
        scope_ccai_tests_restclient(sequencer)

    return

def scope_ccai_tests_restclient(sequencer):
    """
    This is the entry point for the 'ccai_tests_restclient' test scope.
    """

    with sequencer.enter_module_scope_context("ccai.tests.restclient") as msc:
        scope_ccai_tests_restclient_nebius(sequencer)

    return

def scope_ccai_tests_restclient_nebius(sequencer):
    """
    This is the entry point for the 'ccai_tests_restclient_nebius' test scope.
    """

    with sequencer.enter_module_scope_context("ccai.tests.restclient.nebius") as msc:
        scope_ccai_tests_restclient_nebius_test_apigroups(sequencer)
        scope_ccai_tests_restclient_nebius_test_authentication(sequencer)
        scope_ccai_tests_restclient_nebius_test_groupsupport_paging(sequencer)
        scope_ccai_tests_restclient_nebius_test_properties(sequencer)
        scope_ccai_tests_restclient_nebius_test_smoke_live(sequencer)
        scope_ccai_tests_restclient_nebius_test_taskhandle(sequencer)

    return

def scope_ccai_tests_restclient_nebius_test_apigroups(sequencer):
    """
    This is the entry point for the 'ccai_tests_restclient_nebius_test_apigroups' test scope.
    """

    with sequencer.enter_module_scope_context("ccai.tests.restclient.nebius.test_apigroups") as msc:
        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_apply_tags_translates_neutral_shape ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_apply_tags_translates_neutral_shape"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_apply_tags_translates_neutral_shape

            test_apply_tags_translates_neutral_shape()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_create_disk_returns_task_handle ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_create_disk_returns_task_handle"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_create_disk_returns_task_handle

            test_create_disk_returns_task_handle()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_create_placement_group_with_infiniband ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_create_placement_group_with_infiniband"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_create_placement_group_with_infiniband

            test_create_placement_group_with_infiniband()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_create_security_group_idempotent ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_create_security_group_idempotent"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_create_security_group_idempotent

            test_create_security_group_idempotent()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_create_subnet_accepts_contained_cidr ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_create_subnet_accepts_contained_cidr"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_create_subnet_accepts_contained_cidr

            test_create_subnet_accepts_contained_cidr()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_create_subnet_rejects_uncontained_cidr ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_create_subnet_rejects_uncontained_cidr"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_create_subnet_rejects_uncontained_cidr

            test_create_subnet_rejects_uncontained_cidr()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_create_vpc_is_idempotent_by_name ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_create_vpc_is_idempotent_by_name"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_create_vpc_is_idempotent_by_name

            test_create_vpc_is_idempotent_by_name()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_create_vpc_posts_when_absent ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_create_vpc_posts_when_absent"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_create_vpc_posts_when_absent

            test_create_vpc_posts_when_absent()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_delete_unknown_id_is_no_op ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_delete_unknown_id_is_no_op"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_delete_unknown_id_is_no_op

            test_delete_unknown_id_is_no_op()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_filesystem_and_mount_target_lifecycle ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_filesystem_and_mount_target_lifecycle"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_filesystem_and_mount_target_lifecycle

            test_filesystem_and_mount_target_lifecycle()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_launch_vm_rejects_unavailable_gpu_platform ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_launch_vm_rejects_unavailable_gpu_platform"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_launch_vm_rejects_unavailable_gpu_platform

            test_launch_vm_rejects_unavailable_gpu_platform()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_launch_vm_returns_model_and_handle ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_launch_vm_returns_model_and_handle"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_launch_vm_returns_model_and_handle

            test_launch_vm_returns_model_and_handle()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_list_projects_follows_paging_cursor ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_list_projects_follows_paging_cursor"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_list_projects_follows_paging_cursor

            test_list_projects_follows_paging_cursor()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_register_ssh_key_idempotent ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_register_ssh_key_idempotent"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_register_ssh_key_idempotent

            test_register_ssh_key_idempotent()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_apigroups#test_terminate_vm_idempotent_on_404 ================

        test_scope_name = "ccai.tests.restclient.nebius.test_apigroups#test_terminate_vm_idempotent_on_404"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_apigroups import test_terminate_vm_idempotent_on_404

            test_terminate_vm_idempotent_on_404()


    return

def scope_ccai_tests_restclient_nebius_test_authentication(sequencer):
    """
    This is the entry point for the 'ccai_tests_restclient_nebius_test_authentication' test scope.
    """

    with sequencer.enter_module_scope_context("ccai.tests.restclient.nebius.test_authentication") as msc:
        # ================ Test Scope: ccai.tests.restclient.nebius.test_authentication#test_403_reclassified ================

        test_scope_name = "ccai.tests.restclient.nebius.test_authentication#test_403_reclassified"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_authentication import test_403_reclassified

            test_403_reclassified()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_authentication#test_construction_rejects_non_nebius_credential ================

        test_scope_name = "ccai.tests.restclient.nebius.test_authentication#test_construction_rejects_non_nebius_credential"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_authentication import test_construction_rejects_non_nebius_credential

            test_construction_rejects_non_nebius_credential()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_authentication#test_failed_exchange_raises_authentication_error ================

        test_scope_name = "ccai.tests.restclient.nebius.test_authentication#test_failed_exchange_raises_authentication_error"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_authentication import test_failed_exchange_raises_authentication_error

            test_failed_exchange_raises_authentication_error()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_authentication#test_jwt_exchange_mints_token_and_injects_bearer ================

        test_scope_name = "ccai.tests.restclient.nebius.test_authentication#test_jwt_exchange_mints_token_and_injects_bearer"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_authentication import test_jwt_exchange_mints_token_and_injects_bearer

            test_jwt_exchange_mints_token_and_injects_bearer()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_authentication#test_persistent_401_reclassified ================

        test_scope_name = "ccai.tests.restclient.nebius.test_authentication#test_persistent_401_reclassified"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_authentication import test_persistent_401_reclassified

            test_persistent_401_reclassified()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_authentication#test_token_reminted_when_expired ================

        test_scope_name = "ccai.tests.restclient.nebius.test_authentication#test_token_reminted_when_expired"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_authentication import test_token_reminted_when_expired

            test_token_reminted_when_expired()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_authentication#test_token_reused_within_lifetime ================

        test_scope_name = "ccai.tests.restclient.nebius.test_authentication#test_token_reused_within_lifetime"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_authentication import test_token_reused_within_lifetime

            test_token_reused_within_lifetime()


    return

def scope_ccai_tests_restclient_nebius_test_groupsupport_paging(sequencer):
    """
    This is the entry point for the 'ccai_tests_restclient_nebius_test_groupsupport_paging' test scope.
    """

    with sequencer.enter_module_scope_context("ccai.tests.restclient.nebius.test_groupsupport_paging") as msc:
        # ================ Test Scope: ccai.tests.restclient.nebius.test_groupsupport_paging#test_iter_pages_raises_on_cursor_cycle ================

        test_scope_name = "ccai.tests.restclient.nebius.test_groupsupport_paging#test_iter_pages_raises_on_cursor_cycle"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_groupsupport_paging import test_iter_pages_raises_on_cursor_cycle

            test_iter_pages_raises_on_cursor_cycle()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_groupsupport_paging#test_iter_pages_terminates_on_empty_cursor ================

        test_scope_name = "ccai.tests.restclient.nebius.test_groupsupport_paging#test_iter_pages_terminates_on_empty_cursor"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_groupsupport_paging import test_iter_pages_terminates_on_empty_cursor

            test_iter_pages_terminates_on_empty_cursor()


    return

def scope_ccai_tests_restclient_nebius_test_properties(sequencer):
    """
    This is the entry point for the 'ccai_tests_restclient_nebius_test_properties' test scope.
    """

    with sequencer.enter_module_scope_context("ccai.tests.restclient.nebius.test_properties") as msc:
        # ================ Test Scope: ccai.tests.restclient.nebius.test_properties#test_cidr_containment_rejects_unparseable ================

        test_scope_name = "ccai.tests.restclient.nebius.test_properties#test_cidr_containment_rejects_unparseable"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_properties import test_cidr_containment_rejects_unparseable

            test_case_name = "ccai.tests.restclient.nebius.test_properties#test_cidr_containment_rejects_unparseable"

            sequencer.run_property_test(test_cidr_containment_rejects_unparseable, test_case_name, tscope.recorder, tscope.scope_id, {})

        # ================ Test Scope: ccai.tests.restclient.nebius.test_properties#test_compose_leaf_is_deterministic_and_segmented ================

        test_scope_name = "ccai.tests.restclient.nebius.test_properties#test_compose_leaf_is_deterministic_and_segmented"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_properties import test_compose_leaf_is_deterministic_and_segmented

            test_case_name = "ccai.tests.restclient.nebius.test_properties#test_compose_leaf_is_deterministic_and_segmented"

            sequencer.run_property_test(test_compose_leaf_is_deterministic_and_segmented, test_case_name, tscope.recorder, tscope.scope_id, {})

        # ================ Test Scope: ccai.tests.restclient.nebius.test_properties#test_compose_leaf_rejects_empty_segment ================

        test_scope_name = "ccai.tests.restclient.nebius.test_properties#test_compose_leaf_rejects_empty_segment"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_properties import test_compose_leaf_rejects_empty_segment

            test_case_name = "ccai.tests.restclient.nebius.test_properties#test_compose_leaf_rejects_empty_segment"

            sequencer.run_property_test(test_compose_leaf_rejects_empty_segment, test_case_name, tscope.recorder, tscope.scope_id, {})

        # ================ Test Scope: ccai.tests.restclient.nebius.test_properties#test_idempotent_create_never_posts_when_present ================

        test_scope_name = "ccai.tests.restclient.nebius.test_properties#test_idempotent_create_never_posts_when_present"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_properties import test_idempotent_create_never_posts_when_present

            test_case_name = "ccai.tests.restclient.nebius.test_properties#test_idempotent_create_never_posts_when_present"

            sequencer.run_property_test(test_idempotent_create_never_posts_when_present, test_case_name, tscope.recorder, tscope.scope_id, {})

        # ================ Test Scope: ccai.tests.restclient.nebius.test_properties#test_paging_traversal_visits_every_item ================

        test_scope_name = "ccai.tests.restclient.nebius.test_properties#test_paging_traversal_visits_every_item"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_properties import test_paging_traversal_visits_every_item

            test_case_name = "ccai.tests.restclient.nebius.test_properties#test_paging_traversal_visits_every_item"

            sequencer.run_property_test(test_paging_traversal_visits_every_item, test_case_name, tscope.recorder, tscope.scope_id, {})

        # ================ Test Scope: ccai.tests.restclient.nebius.test_properties#test_subnet_of_parent_is_contained ================

        test_scope_name = "ccai.tests.restclient.nebius.test_properties#test_subnet_of_parent_is_contained"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_properties import test_subnet_of_parent_is_contained

            test_case_name = "ccai.tests.restclient.nebius.test_properties#test_subnet_of_parent_is_contained"

            sequencer.run_property_test(test_subnet_of_parent_is_contained, test_case_name, tscope.recorder, tscope.scope_id, {})

        # ================ Test Scope: ccai.tests.restclient.nebius.test_properties#test_wait_returns_first_terminal_state ================

        test_scope_name = "ccai.tests.restclient.nebius.test_properties#test_wait_returns_first_terminal_state"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_properties import test_wait_returns_first_terminal_state

            test_case_name = "ccai.tests.restclient.nebius.test_properties#test_wait_returns_first_terminal_state"

            sequencer.run_property_test(test_wait_returns_first_terminal_state, test_case_name, tscope.recorder, tscope.scope_id, {})


    return

def scope_ccai_tests_restclient_nebius_test_smoke_live(sequencer):
    """
    This is the entry point for the 'ccai_tests_restclient_nebius_test_smoke_live' test scope.
    """

    with sequencer.enter_module_scope_context("ccai.tests.restclient.nebius.test_smoke_live") as msc:
        # ================ Test Scope: ccai.tests.restclient.nebius.test_smoke_live#test_live_list_projects ================

        test_scope_name = "ccai.tests.restclient.nebius.test_smoke_live#test_live_list_projects"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_smoke_live import test_live_list_projects

            test_live_list_projects(live_client)


    return

def scope_ccai_tests_restclient_nebius_test_taskhandle(sequencer):
    """
    This is the entry point for the 'ccai_tests_restclient_nebius_test_taskhandle' test scope.
    """

    with sequencer.enter_module_scope_context("ccai.tests.restclient.nebius.test_taskhandle") as msc:
        # ================ Test Scope: ccai.tests.restclient.nebius.test_taskhandle#test_done_flag_without_explicit_status ================

        test_scope_name = "ccai.tests.restclient.nebius.test_taskhandle#test_done_flag_without_explicit_status"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_taskhandle import test_done_flag_without_explicit_status

            test_done_flag_without_explicit_status()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_taskhandle#test_task_handle_rejects_empty_operation_id ================

        test_scope_name = "ccai.tests.restclient.nebius.test_taskhandle#test_task_handle_rejects_empty_operation_id"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_taskhandle import test_task_handle_rejects_empty_operation_id

            test_task_handle_rejects_empty_operation_id()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_taskhandle#test_wait_reaches_done_after_running_states ================

        test_scope_name = "ccai.tests.restclient.nebius.test_taskhandle#test_wait_reaches_done_after_running_states"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_taskhandle import test_wait_reaches_done_after_running_states

            test_wait_reaches_done_after_running_states()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_taskhandle#test_wait_terminates_on_failed ================

        test_scope_name = "ccai.tests.restclient.nebius.test_taskhandle#test_wait_terminates_on_failed"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_taskhandle import test_wait_terminates_on_failed

            test_wait_terminates_on_failed()

        # ================ Test Scope: ccai.tests.restclient.nebius.test_taskhandle#test_wait_times_out_when_never_terminal ================

        test_scope_name = "ccai.tests.restclient.nebius.test_taskhandle#test_wait_times_out_when_never_terminal"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from ccai.tests.restclient.nebius.test_taskhandle import test_wait_times_out_when_never_terminal

            test_wait_times_out_when_never_terminal()


    return
