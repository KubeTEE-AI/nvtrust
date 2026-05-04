#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-FileCopyrightText: Copyright (c) 2021-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import subprocess
import os
from nv_attestation_sdk.attestation import Attestation

@pytest.mark.gpu_hardware
@pytest.mark.switch_hardware
@pytest.mark.user_mode
def test_successful_local_ppcie_attestation(rim_url, ocsp_url):
    invoke_attestation(rim_url, ocsp_url, attestation_mode="LOCAL")

@pytest.mark.gpu_hardware
@pytest.mark.switch_hardware
@pytest.mark.user_mode
def test_successful_remote_ppcie_attestation(rim_url, ocsp_url):
    invoke_attestation(rim_url, ocsp_url, attestation_mode="REMOTE")

@pytest.mark.gpu_hardware
@pytest.mark.switch_hardware
@pytest.mark.user_mode
def test_successful_local_ppcie_attestation_with_valid_service_key(service_key, rim_url, ocsp_url):
    if not service_key:
        pytest.skip("Service key not provided")
    invoke_attestation(rim_url, ocsp_url, service_key=service_key, attestation_mode="LOCAL")

@pytest.mark.gpu_hardware
@pytest.mark.switch_hardware
@pytest.mark.user_mode
def test_fail_local_ppcie_attestation_with_invalid_service_key(rim_url, ocsp_url):
    invoke_attestation(rim_url, ocsp_url, service_key="SOME_INVALID_SERVICE_KEY", attestation_mode="LOCAL", expect_ready=False)

@pytest.mark.gpu_hardware
@pytest.mark.switch_hardware
@pytest.mark.user_mode
def test_successful_remote_ppcie_attestation_with_valid_service_key(service_key, rim_url, ocsp_url):
    if not service_key:
        pytest.skip("Service key not provided")
    invoke_attestation(rim_url, ocsp_url, service_key=service_key, attestation_mode="REMOTE")

@pytest.mark.gpu_hardware
@pytest.mark.switch_hardware
@pytest.mark.user_mode
def test_fail_remote_ppcie_attestation_with_invalid_service_key(rim_url, ocsp_url):
    invoke_attestation(rim_url, ocsp_url, service_key="SOME_INVALID_SERVICE_KEY", attestation_mode="REMOTE", expect_ready=False)

@pytest.mark.gpu_hardware
@pytest.mark.switch_hardware
@pytest.mark.user_mode
def test_fail_with_invalid_combination_of_mode():
    command = [
        'python3',
        '-m',
        'ppcie.verifier.verification',
        '--gpu-attestation-mode',
        "LOCAL",
        '--switch-attestation-mode',
        "REMOTE",
        '--claims-version',
        "2.0"
    ]
    invoke_attestation_with_command(command, expect_ready=False)

def invoke_attestation(rim_url, ocsp_url, service_key=None, attestation_mode="LOCAL", expect_ready=True):
    command = [
        'python3',
        '-m',
        'ppcie.verifier.verification',
        '--gpu-attestation-mode',
        attestation_mode,
        '--switch-attestation-mode',
        attestation_mode,
        '--claims-version',
        "2.0",
        '--rim-url',
        rim_url,
        '--ocsp-url',
        ocsp_url
    ]

    if service_key is not None:
        command.extend(['--service_key', service_key])

    invoke_attestation_with_command(command, expect_ready=expect_ready)

def invoke_attestation_with_command(command, env=None, expect_ready=True):
    result = subprocess.run(command, capture_output=True, text=True, env=env)

    assert result.returncode == 0

    success_indicators = [
        "PPCIE: GPU state is READY",
        "PPCIE: Successfully set gpu state to True",
        "PPCIE: Failed to set GPU ready state since terminal state has been reached"
    ]

    if expect_ready:
        assert any(indicator in result.stdout for indicator in success_indicators)
    else:
        assert not any(indicator in result.stdout for indicator in success_indicators)

@pytest.fixture(autouse=True)
def reset():
    yield
    Attestation.reset()
