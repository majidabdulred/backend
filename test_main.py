from fastapi.testclient import TestClient
from aws import aws_client

from main import app

client = TestClient(app)

# def test_read_main():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"message": "Hello World"}


def test_create_session():
    response = client.post("/v2/session/create",json={"gpu_uuid":"test-uuid",
                                                      "gpu_name":"NVIDIA GeForce RTX 3060 Laptop GPU",
                                                      "gpu_total_memory": 6144,})
    assert len(response.json().get("host_session_id")) == 24
    assert response.status_code == 200


def test_ping_session():
    response = client.post("/v2/session/ping",headers={"host-session-id":"test-uuid","version":"1.0"})
    assert response.json() == {"success": True}
    assert response.status_code == 200


def test_assign_request():
    response = client.post("/v2/request/assign",headers={"host-session-id":"63a8a45517f6bbf76ab679a0","version":"1.0"})
    custom_request_keys = ['session_id', 'request_type', 'prompt', 'seed', 'sampler_name', 'batch_size', 'steps', 'cfg_scale', 'width', 'height', 'negative_prompt']
    no_available_request_keys = ['detail']
    assert list(response.json().keys()) in [custom_request_keys, no_available_request_keys]
    assert response.status_code in (200,404)


def test_submit_request():
    base64_str = open("app/testimage.txt", "r").read()
    response = client.post("/v2/request/submit",headers={"host-session-id":"63a8a45517f6bbf76ab679a0","version":"1.0"},
                           json={"session_id":"63a8b1c8c1eb2d0a7f09f5de","file":base64_str})
    assert response.json() == {"success": True}
    assert response.status_code == 200
