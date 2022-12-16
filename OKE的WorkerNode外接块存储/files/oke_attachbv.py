#!/usr/bin/env python3
# uncoding=utf-8

# coding: utf-8
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.


import json

import oci
import sys
import time
import os.path

sizeInGB = sys.argv[1]
vpu = sys.argv[2]


def create_volume(block_storage, compartment_id, availability_domain, display_name):
    result = block_storage.create_volume(
        oci.core.models.CreateVolumeDetails(
            compartment_id=compartment_id,
            availability_domain=availability_domain,
            size_in_gbs=int(sizeInGB),
            vpus_per_gb=int(vpu),
            display_name=display_name
        )
    )
    volume = oci.wait_until(
        block_storage,
        block_storage.get_volume(result.data.id),
        'lifecycle_state',
        'AVAILABLE'
    ).data
    print('Created Volume: {}'.format(display_name))

    return volume


def get_image(compute, compartment_id, operating_system, os_version, target_shape):
    images = oci.pagination.list_call_get_all_results(
        compute.list_images,
        compartment_id,
        operating_system=operating_system,
        operating_system_version=os_version
    ).data
    # oci.pagination.li

    for img in images:
        shapes_for_image = oci.pagination.list_call_get_all_results(
            compute.list_shapes,
            compartment_id,
            image_id=img.id
        ).data

        for s in shapes_for_image:
            if s.shape == target_shape:
                return img

    raise RuntimeError('No valid image found for target OS, Version and Shape')


signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

# In the base case, configuration does not need to be provided as the region and tenancy are obtained from the InstancePrincipalsSecurityTokenSigner
identity_client = oci.identity.IdentityClient(config={}, signer=signer)
compute_client = oci.core.ComputeClient(config={}, signer=signer)
virtual_network_client = oci.core.VirtualNetworkClient(config={}, signer=signer)
block_storage_client = oci.core.BlockstorageClient(config={}, signer=signer)

vcn_and_subnet = None
volume_one = None
volume_two = None
instance = None
try:
    import json

    import requests as req

    r = req.get('http://169.254.169.254/opc/v1/instance')
    metastr = r.text

    jsonvm = json.loads(metastr)
    instance_ocid = jsonvm['id']
    compartment_id = jsonvm['compartmentId']
    availability_domain = jsonvm['availabilityDomain']
    volume_one = create_volume(block_storage_client, compartment_id, availability_domain, 'okeAddVolume')

    paravirtualized_volume_attachment_response = compute_client.attach_volume(
        oci.core.models.AttachParavirtualizedVolumeDetails(
            display_name='ParavirtualizedVolAttachment',
            instance_id=instance_ocid,
            volume_id=volume_one.id
        )
    )
    print('Attached paravirtualized volume')
    print('')

    oci.wait_until(
        compute_client,
        compute_client.get_volume_attachment(paravirtualized_volume_attachment_response.data.id),
        'lifecycle_state',
        'ATTACHED'
    )





finally:
    print('')

print('Script Finished')
