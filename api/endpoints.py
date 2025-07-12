from fastapi import APIRouter, Response, BackgroundTasks, HTTPException
from io import StringIO
from pydantic import BaseModel, Field
from typing import Optional

import bw2data as bd
from brightwebapp.brightway import load_and_set_useeio_project, load_and_set_ecoinvent_project
from brightwebapp.traversal import perform_graph_traversal

router = APIRouter()


class SetupResponse(BaseModel):
    """Response model for the setup endpoint."""
    status: str
    message: str


class EcoinventSetupRequest(BaseModel):
    """
    Represents a request for setting up the ecoinvent database.

    This model defines the structure for providing credentials required
    to download and install the ecoinvent database if it is not already
    present in the Brightway project list.

    Attributes
    ----------
    username: str, optional
        The username for your ecoinvent account. Required only if the
        database needs to be downloaded.
    password: str, optional
        The password for your ecoinvent account. Required only if the
        database needs to be downloaded.
    """
    username: Optional[str] = Field(None, description="Ecoinvent username")
    password: Optional[str] = Field(None, description="Ecoinvent password")


@router.post(
    "/setup/useeio-database",
    status_code=202,
    response_model=SetupResponse,
    responses={
        202: {
            "description": "Confirmation that the setup task has been scheduled.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "accepted",
                        "message": "The USEEIO-1.1 database setup has been scheduled. This may take several minutes."
                    }
                }
            }
        }
    }
)
async def setup_useeio_database(background_tasks: BackgroundTasks):
    """
    Schedules the USEEIO database setup as a background task.

    This endpoint initiates a long-running process to download and install
    the USEEIO-1.1 database if it is not already present. To avoid
    request timeouts, the task is scheduled to run in the background.
    The API responds immediately with a task ID, which can be used to
    poll a status endpoint for completion.

    See Also
    --------
    [`brightwebapp.brightway.load_and_set_useeio_project`](https://brightwebapp.readthedocs.io/en/latest/api/brightway/#brightwebapp.brightway.load_and_set_useeio_project)
    ```
    """
    background_tasks.add_task(load_and_set_useeio_project)
    return {
        "status": "accepted",
        "message": "The USEEIO-1.1 database setup has been scheduled. This may take several minutes."
    }


@router.post(
    "/setup/ecoinvent-database",
    status_code=202,
    response_model=SetupResponse,
    responses={
        202: {
            "description": "Confirmation that the ecoinvent setup task has been scheduled.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "accepted",
                        "message": "The ecoinvent database setup has been scheduled. This may take several minutes."
                    }
                }
            }
        },
        400: {
            "description": "Raised if the ecoinvent database needs to be downloaded but username and password are not provided.",
            "content": {
                "application/json": {
                    "example": {"detail": "Ecoinvent credentials are required but were not provided."}
                }
            }
        }
    }
)
async def setup_ecoinvent_database(
    request: EcoinventSetupRequest, background_tasks: BackgroundTasks
):
    """
    Schedules the ecoinvent 3.10 database setup as a background task.

    This endpoint initiates the process to install the ecoinvent 3.10
    database. If the database is not already installed, it will be
    downloaded from the ecoinvent servers, which is a long-running task.
    The process is run in the background to avoid request timeouts.

    Notes
    -----
    Ecoinvent credentials are required if the database is not already installed.

    See Also
    --------
    [`brightwebapp.brightway.load_and_set_ecoinvent_project`](https://brightwebapp.readthedocs.io/en/latest/api/brightway/#brightwebapp.brightway.load_and_set_ecoinvent_project)
    """
    if "ei_3_10" not in bd.projects:
        if not request.username or not request.password:
            raise HTTPException(
                status_code=400,
                detail="Ecoinvent project 'ei_3_10' is not installed. Please provide username and password to download it.",
            )

    background_tasks.add_task(
        load_and_set_ecoinvent_project,
        username=request.username,
        password=request.password,
    )

    return {
        "status": "accepted",
        "message": "The ecoinvent 3.10 database setup has been scheduled. This may take several minutes.",
    }


class DemandItem(BaseModel):
    """
    Represents a single functional unit in a demand request.

    This model defines the structure for one item in the `demand` list
    of a graph traversal request. It specifies the unique code of an
    activity and the amount to be assessed.

    Attributes
    ----------
    code: str
        The unique string identifier (code) for the activity node in the Brightway database.
    amount: float
        The functional unit amount for this activity.

    Example
    -------
    This is how a single demand item should be formatted in your JSON request:

    ```json
    {
        "code": "some_valid_code_in_your_db",
        "amount": 1.0
    }
    ```
    """
    code: str
    amount: float


class GraphTraversalRequest(BaseModel):
    """
    Represents a request for performing a graph traversal.

    This model defines the structure for a detailed request body
    to perform a graph traversal in the Brightway database. It includes
    a list of demand items, the method for impact assessment, and
    various parameters for the traversal.

    Attributes
    ----------
    demand: list[DemandItem]
        A list of demand items, each specifying a unique code and the amount to be assessed.
    method: tuple
        A tuple specifying the impact assessment method, e.g., ('IMPACT World+ Midpoint', 'Climate change', 'GWP100').
    cutoff: float
        The cutoff threshold for the graph traversal, default is 0.001.
    biosphere_cutoff: float
        The biosphere cutoff threshold for the graph traversal, default is 0.001.
    max_calc: int
        The maximum number of calculations to perform during the traversal, default is 100.
    
    Example
    -------
    This is how a graph traversal request should be formatted in your JSON body:

    ```json
    {
        "demand": [
            {
                "code": "some_valid_code_in_your_db",
                "amount": 1.0
            }
        ],
        "method": ["IMPACT World+ Midpoint", "Climate change", "GWP100"],
        "cutoff": 0.001,
        "biosphere_cutoff": 0.001,
        "max_calc": 100
    }
    ```
    """
    demand: list[DemandItem]
    method: tuple # Example: ('IMPACT World+ Midpoint', 'Climate change', 'GWP100')
    cutoff: float = 0.001
    biosphere_cutoff: float = 0.001
    max_calc: int = 100


@router.post(
    "/traversal/perform",
    response_class=Response,
    responses={
        200: {
            "description": "On success, a streaming response containing the graph traversal data as a CSV file.",
            "content": {
                "text/csv": {
                    "schema": {
                        "type": "string",
                        "format": "binary",
                    },
                    "example": "UID,Scope,Name,SupplyAmount,...\n0,1,Activity A,1.0,...\n1,3,Activity B,0.5,..."
                }
            }
        },
        400: {
            "description": "Raised if the cutoff value is too high and no graph edges are found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No edges found in the graph traversal. This may be due to a cutoff value that is too high, or a demand that does not lead to any edges."
                    }
                }
            }
        },
        500: {
            "description": "Raised for other unexpected exceptions, such as a missing demand code.",
             "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred: Node not found for code 'some_invalid_code'"
                    }
                }
            }
        }
    }
)
async def run_graph_traversal(request: GraphTraversalRequest):
    """
    Performs a graph traversal and returns the result as a CSV file.

    This endpoint serves as the primary calculation interface. It accepts a
    detailed JSON object specifying the demand, method, and calculation
    parameters. Upon success, it directly returns a CSV file for download.

    See Also
    --------
    [`brightwebapp.traversal.perform_graph_traversal`](https://brightwebapp.readthedocs.io/en/latest/api/traversal/#brightwebapp.traversal.perform_graph_traversal)
    """
    try:
        demand_dict = {
            bd.get_node(code=item.code): item.amount for item in request.demand
        }

        csv_data = perform_graph_traversal(
            demand=demand_dict,
            method=request.method,
            cutoff=request.cutoff,
            biosphere_cutoff=request.biosphere_cutoff,
            max_calc=request.max_calc,
            return_format='csv'
        )

        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=graph_traversal.csv"
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
