#!/usr/bin/env python
# -*- coding: utf-8 -*-


#!/usr/bin/env python
# VMware vSphere Python SDK
# Copyright (c) 2008-2013 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Python program for listing the vms on an ESX / vCenter host
"""
from __future__ import print_function

import sys
import atexit
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
from pyVim.task import WaitForTask
import VMBR_APP.vm_config



def get_vm_info(virtual_machine):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    """
    vm_info = {}
    summary = virtual_machine.summary
    print("Name       : ", summary.config.name)
    print("Template   : ", summary.config.template)
    print("Path       : ", summary.config.vmPathName)
    print("Guest      : ", summary.config.guestFullName)
    print("Instance UUID : ", summary.config.instanceUuid)
    print("Bios UUID     : ", summary.config.uuid)
    vm_info = {
        "Name": summary.config.name,
        "Template": summary.config.template,
        "Path": summary.config.vmPathName,
        "Guest": summary.config.guestFullName,
        "IUUID": summary.config.instanceUuid,
        "BUUID": summary.config.uuid
    }
    annotation = summary.config.annotation
    if annotation:
        print("Annotation : ", annotation)
        vm_info["Annotation"] = annotation
    print("State      : ", summary.runtime.powerState)
    vm_info["State"] = summary.runtime.powerState
    if summary.guest is not None:
        ip_address = summary.guest.ipAddress
        tools_version = summary.guest.toolsStatus
        if tools_version is not None:
            print("VMware-tools: ", tools_version)
            vm_info["VMware-tools"] = tools_version
        else:
            print("Vmware-tools: None")
            vm_info["VMware-tools"] = None
        if ip_address:
            print("IP         : ", ip_address)
            vm_info["IP"] = ip_address
        else:
            print("IP         : None")
            vm_info["IP"] = None
    if summary.runtime.question is not None:
        print("Question  : ", summary.runtime.question.text, "")
        vm_info["Question"] = summary.runtime.question.text
    return vm_info


def connect_vm(host, user, password, port=443):
    """
    Simple connect the virtual machines on a system.
    """
    service_instance = None
    try:
        '''
        if args.disable_ssl_verification:
            service_instance = connect.SmartConnectNoSSL(host=host,
                                                         user=user,
                                                         pwd=password,
                                                         port=int(port))
        else:
        service_instance = connect.SmartConnect(host=host,
                                                user=user,
                                                pwd=password,
                                                port=int(port))
        '''
        service_instance = connect.SmartConnectNoSSL(host=host,
                                                        user=user,
                                                        pwd=password,
                                                        port=int(port))
        atexit.register(connect.Disconnect, service_instance)
    except IOError:
        pass 
    if not service_instance:
        raise SystemExit("Unable to connect to host with supplied info.")
        return None
    else:
        return service_instance


def get_all_vms():
    args = vm_config
    service_instance = connect_vm(args.host, args.user, args.password, args.port)
    try:
        vms_list = []
        content = service_instance.RetrieveContent()
        container = content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)

        children = containerView.view
        for child in children:
            vm_info = get_vm_info(child)
            vms_list.extend(vm_info)
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return False
    else:
        return vms_list



def operation_snapshots(vm_name, snapshot_name, operation):
    si = None
    args = vm_config
    print("Trying to connect to VCENTER SERVER . . .")
    si = connect_vm(args.host, args.user, args.password, args.port)
    if si:
        print("Connected to VCENTER SERVER !")
    else:
        print("Trying to connect to VCENTER SERVER ERROR!!!. . .")

    content = si.RetrieveContent()

    vm = get_obj(content, [vim.VirtualMachine], vm_name)

    if not vm:
        print("Virtual Machine %s doesn't exists" % vm_name)
        sys.exit()

    if operation != 'create' and vm.snapshot is None:
        print("Virtual Machine %s doesn't have any snapshots" % vm.name)
        sys.exit()

    if operation == 'list_current':
        try:
            current_snapshot_dict = {}
            current_snapref = vm.snapshot.currentSnapshot
            current_snap_obj = get_current_snap_obj(
                                vm.snapshot.rootSnapshotList, current_snapref)
            current_snapshot = "Name: %s; Description: %s; " \
                            "CreateTime: %s; State: %s" % (
                                    current_snap_obj[0].name,
                                    current_snap_obj[0].description,
                                    current_snap_obj[0].createTime,
                                    current_snap_obj[0].state)
        except Exception as err:
            print(str(err))
            return False
        else:
            current_snapshot_dict = {
                "Name": current_snap_obj[0].name,
                "Description": current_snap_obj[0].description,
                "CreateTime": current_snap_obj[0].createTime,
                "State": current_snap_obj[0].state
            }
            print("Virtual machine %s current snapshot is:" % vm.name)
            print(current_snapshot)
            return current_snapshot_dict

    elif operation == 'list_all':
        print("Display list of snapshots on virtual machine %s" % vm.name)
        try:
            snapshot_list = []
            snapshot_paths = list_snapshots_recursively(
                                vm.snapshot.rootSnapshotList)
            for snapshot in snapshot_paths:
                print(snapshot)
                snapshot_list.extend(snapshot)
        except Exception as err:
            print(str(err))
            return False
        else:
            return snapshot_list

    elif operation == 'create':
        try:
            description = "Test snapshot"
            dumpMemory = False
            quiesce = False

            print("Creating snapshot %s for virtual machine %s" % (
                                            snapshot_name, vm.name))
            WaitForTask(vm.CreateSnapshot(
                snapshot_name, description, dumpMemory, quiesce))
        except Exception as err:
            print(str(err))
            return False
        else:
            return True

    elif operation in ['remove', 'revert']:
        try:
            snap_obj = get_snapshots_by_name_recursively(
                                vm.snapshot.rootSnapshotList, snapshot_name)
            # if len(snap_obj) is 0; then no snapshots with specified name
            if len(snap_obj) == 1:
                snap_obj = snap_obj[0].snapshot
                try:
                    if operation == 'remove':
                        print("Removing snapshot %s" % snapshot_name)
                        WaitForTask(snap_obj.RemoveSnapshot_Task(True))
                    else:
                        print("Reverting to snapshot %s" % snapshot_name)
                        WaitForTask(snap_obj.RevertToSnapshot_Task())
                except Exception as err:
                    print(str(err))
                    return False
            else:
                print("No snapshots found with name: %s on VM: %s" % (
                                                    snapshot_name, vm.name))
                return False
        except Exception as err:
            print(str(err))
            return False
        else:
            return True

    elif operation == 'remove_all':
        print("Removing all snapshots for virtual machine %s" % vm.name)
        try:
            WaitForTask(vm.RemoveAllSnapshots())
        except Exception as err:
            print(str(err))
            return False
        else:
            return True
    else:
        print("Specify operation in "
              "create/remove/revert/list_all/list_current/remove_all")
        return False

def get_obj(content, vimtype, name):
    """
     Get the vsphere object associated with a given text name
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def list_snapshots_recursively(snapshots):
    snapshot_data = []
    snap_text = ""
    for snapshot in snapshots:
        snap_text = "Name: %s; Description: %s; CreateTime: %s; State: %s" % (
                                        snapshot.name, snapshot.description,
                                        snapshot.createTime, snapshot.state)
        snapshot_data.append(snap_text)
        snapshot_data = snapshot_data + list_snapshots_recursively(
                                        snapshot.childSnapshotList)
    return snapshot_data


def get_snapshots_by_name_recursively(snapshots, snapname):
    snap_obj = []
    for snapshot in snapshots:
        if snapshot.name == snapname:
            snap_obj.append(snapshot)
        else:
            snap_obj = snap_obj + get_snapshots_by_name_recursively(
                                    snapshot.childSnapshotList, snapname)
    return snap_obj


def get_current_snap_obj(snapshots, snapob):
    snap_obj = []
    for snapshot in snapshots:
        if snapshot.snapshot == snapob:
            snap_obj.append(snapshot)
        snap_obj = snap_obj + get_current_snap_obj(
                                snapshot.childSnapshotList, snapob)
    return snap_obj