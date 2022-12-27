from fastapi.testclient import TestClient
from aws import aws_client
from dotenv import load_dotenv
from main import app
import pytest

client = TestClient(app)
load_dotenv()




def test_create_session():
    response = client.post("/v2/session/create", json={"gpu_uuid": "test-uuid",
                                                       "gpu_name": "NVIDIA GeForce RTX 3060 Laptop GPU",
                                                       "gpu_total_memory": 6144, })
    assert len(response.json().get("host_session_id")) == 24
    assert response.status_code == 200


def test_ping_session():
    response = client.post("/v2/session/ping", headers={"host-session-id": "test-uuid", "version": "1.0"})
    assert response.json() == {"success": True}
    assert response.status_code == 200


def test_assign_request():
    response = client.post("/v2/request/assign",
                           headers={"host-session-id": "63a8a45517f6bbf76ab679a0", "version": "1.0"})
    custom_request_keys = ['session_id', 'request_type', 'prompt', 'seed', 'sampler_name', 'batch_size', 'steps',
                           'cfg_scale', 'width', 'height', 'negative_prompt']
    no_available_request_keys = ['detail']
    assert list(response.json().keys()) in [custom_request_keys, no_available_request_keys]
    assert response.status_code in (200, 404)


@pytest.mark.asyncio
def test_submit_request():
    base64_str = open("app/testimage.txt", "r").read()
    response = client.post("/v2/request/submit",
                           headers={"host-session-id": "63a8a45517f6bbf76ab679a0", "version": "1.0"},
                           json={"session_id": "63a8b1c8c1eb2d0a7f09f5de", "file": base64_str})
    assert response.json() == {"success": True}
    assert response.status_code == 200

@pytest.mark.full_test
def test_client():
    response = client.post("/v2/session/create", json={"gpu_uuid": "test-uuid",
                                                       "gpu_name": "NVIDIA GeForce RTX 3060 Laptop GPU",
                                                       "gpu_total_memory": 6144, })
    host_session_id = response.json().get("host_session_id")
    assert len(host_session_id) == 24
    assert response.status_code == 200

    response = client.post("/v2/session/ping", headers={"host-session-id": host_session_id, "version": "1.0"})
    assert response.json() == {"success": True}
    assert response.status_code == 200

    response = client.post("/v2/request/assign",
                           headers={"host-session-id": host_session_id, "version": "1.0"})
    custom_request_keys = ['session_id', 'request_type', 'prompt', 'seed', 'sampler_name', 'batch_size', 'steps',
                           'cfg_scale', 'width', 'height', 'negative_prompt']
    upscale_request_keys = ["image", "session_id", "request_type", "resize_mode", "show_extras_results",
                            "upscaling_resize_w", "upscaling_resize_h", "upscaling_resize", "upscaling_crop",
                            "upscaler_1",
                            "upscaler_2", "extras_upscaler_2_visibility", "upscale_first"]
    no_available_request_keys = ['detail']
    assert list(response.json().keys()) in [custom_request_keys, no_available_request_keys, upscale_request_keys]
    assert response.status_code in (200, 404)

    if response.status_code == 404:
        return
    session_id = response.json().get("session_id")
    base64_str = open("app/testimage.txt", "r").read()
    response = client.post("/v2/request/submit",
                           headers={"host-session-id": host_session_id, "version": "1.0"},
                           json={"session_id": session_id, "file": base64_str})
    assert response.json() == {"success": True}
    assert response.status_code == 200
    print("Test passed",session_id)