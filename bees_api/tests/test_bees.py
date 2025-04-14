import pytest
from datetime import date
from httpx import AsyncClient
import json

pytestmark = pytest.mark.asyncio


async def test_add_bee(app_with_test_db: dict, async_client: AsyncClient, auth_headers: dict):
    # Test adding a new bee
    today = date.today().isoformat()
    
    response = await async_client.post(
        "/graphql",
        headers=auth_headers,
        json={
            "query": f"""
            mutation {{
                addBee(
                    name: "Buzzy",
                    origin: "Forest Garden",
                    species: "Honey Bee",
                    capturedDate: "{today}"
                ) {{
                    id
                    name
                    origin
                    species
                    capturedDate
                    imagePath
                }}
            }}
            """
        },
    )
    
    # Check if the response is successful
    assert response.status_code == 200
    
    # Parse the response JSON
    json_response = response.json()
    assert "errors" not in json_response
    assert "data" in json_response
    assert "addBee" in json_response["data"]
    
    # Check the returned bee data
    bee_data = json_response["data"]["addBee"]
    assert bee_data["name"] == "Buzzy"
    assert bee_data["origin"] == "Forest Garden"
    assert bee_data["species"] == "Honey Bee"
    assert bee_data["capturedDate"] == today
    assert bee_data["id"] is not None


async def test_get_bees(app_with_test_db: dict, async_client: AsyncClient, auth_headers: dict):
    # First add a bee
    today = date.today().isoformat()
    
    await async_client.post(
        "/graphql",
        headers=auth_headers,
        json={
            "query": f"""
            mutation {{
                addBee(
                    name: "Buzzy",
                    origin: "Forest Garden",
                    species: "Honey Bee",
                    capturedDate: "{today}"
                ) {{
                    id
                }}
            }}
            """
        },
    )
    
    # Now test getting the list of bees
    response = await async_client.post(
        "/graphql",
        headers=auth_headers,
        json={
            "query": """
            query {
                bees {
                    id
                    name
                    origin
                    species
                    capturedDate
                    imagePath
                }
            }
            """
        },
    )
    
    # Check if the response is successful
    assert response.status_code == 200
    
    # Parse the response JSON
    json_response = response.json()
    assert "errors" not in json_response
    assert "data" in json_response
    assert "bees" in json_response["data"]
    
    # Check that we have one bee in the list
    bees_data = json_response["data"]["bees"]
    assert len(bees_data) >= 1
    
    # Check that our bee is in the list
    bee = next((b for b in bees_data if b["name"] == "Buzzy"), None)
    assert bee is not None
    assert bee["origin"] == "Forest Garden"
    assert bee["species"] == "Honey Bee"


async def test_get_specific_bee(app_with_test_db: dict, async_client: AsyncClient, auth_headers: dict):
    # First add a bee
    today = date.today().isoformat()
    
    add_response = await async_client.post(
        "/graphql",
        headers=auth_headers,
        json={
            "query": f"""
            mutation {{
                addBee(
                    name: "Buzzy",
                    origin: "Forest Garden",
                    species: "Honey Bee",
                    capturedDate: "{today}"
                ) {{
                    id
                    name
                }}
            }}
            """
        },
    )
    
    # Get the ID of the added bee
    bee_id = add_response.json()["data"]["addBee"]["id"]
    
    # Now test getting a specific bee by ID
    response = await async_client.post(
        "/graphql",
        headers=auth_headers,
        json={
            "query": f"""
            query {{
                bee(id: {bee_id}) {{
                    id
                    name
                    origin
                    species
                    capturedDate
                    imagePath
                }}
            }}
            """
        },
    )
    
    # Check if the response is successful
    assert response.status_code == 200
    
    # Parse the response JSON
    json_response = response.json()
    assert "errors" not in json_response
    assert "data" in json_response
    assert "bee" in json_response["data"]
    
    # Check the bee data
    bee_data = json_response["data"]["bee"]
    assert bee_data["id"] == bee_id
    assert bee_data["name"] == "Buzzy"
    assert bee_data["origin"] == "Forest Garden"
    assert bee_data["species"] == "Honey Bee"
    assert bee_data["capturedDate"] == today


async def test_delete_bee(app_with_test_db: dict, async_client: AsyncClient, auth_headers: dict):
    # First add a bee
    today = date.today().isoformat()
    
    add_response = await async_client.post(
        "/graphql",
        headers=auth_headers,
        json={
            "query": f"""
            mutation {{
                addBee(
                    name: "DeleteMe",
                    origin: "Test Garden",
                    species: "Test Bee",
                    capturedDate: "{today}"
                ) {{
                    id
                }}
            }}
            """
        },
    )
    
    # Get the ID of the added bee
    bee_id = add_response.json()["data"]["addBee"]["id"]
    
    # Now test deleting the bee
    response = await async_client.post(
        "/graphql",
        headers=auth_headers,
        json={
            "query": f"""
            mutation {{
                deleteBee(id: {bee_id})
            }}
            """
        },
    )
    
    # Check if the response is successful
    assert response.status_code == 200
    
    # Parse the response JSON
    json_response = response.json()
    assert "errors" not in json_response
    assert "data" in json_response
    assert "deleteBee" in json_response["data"]
    
    # Check that the bee was deleted
    assert json_response["data"]["deleteBee"] is True
    
    # Try to get the deleted bee to confirm it's gone
    response = await async_client.post(
        "/graphql",
        headers=auth_headers,
        json={
            "query": f"""
            query {{
                bee(id: {bee_id}) {{
                    id
                    name
                }}
            }}
            """
        },
    )
    
    # Check that the bee no longer exists
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["data"]["bee"] is None