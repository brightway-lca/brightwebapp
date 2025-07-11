from fastapi import APIRouter, Response, BackgroundTasks, HTTPException
from io import StringIO
from pydantic import BaseModel

import bw2data as bd
from brightwebapp.brightway import load_and_set_useeio_project
from brightwebapp.traversal import perform_graph_traversal

router = APIRouter()


class SetupResponse(BaseModel):
    """Response model for the setup endpoint."""
    status: str
    message: str


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
    "/setup/useeio-database",
    status_code=202, # HTTP 202 Accepted
    response_model=SetupResponse
)
async def setup_useeio_database(background_tasks: BackgroundTasks):
    """
    Schedules the USEEIO database setup as a background task.

    This endpoint initiates a long-running process to download and install
    the USEEIO-1.1 database if it is not already present. To avoid
    request timeouts, the task is scheduled to run in the background.
    The API responds immediately with a task ID, which can be used to
    poll a status endpoint for completion.

    Parameters
    ----------
    background_tasks : BackgroundTasks
        A FastAPI dependency that allows scheduling of background tasks.
        The task is executed *after* the response has been sent. This is
        injected by the framework and not provided by the API user.

    Returns
    -------
    dict
        A dictionary confirming that the task has been accepted for processing.
        
        | key            | value                                                                                     |
        | -------------- | ----------------------------------------------------------------------------------------- |
        | `status`       | `accepted`                                                                                |
        | `message`      | "The USEEIO-1.1 database setup has been scheduled. This may take several minutes."        |

    Notes
    -----
    This function is exposed as a ``POST`` endpoint. It returns an HTTP
    ``202 Accepted`` status code upon successfully scheduling the task.
    This is a "fire-and-forget" operation. Once the task is scheduled,
    the API provides no further status updates or results. To monitor the
    actual progress of the download and installation, you may need to
    check the application's server or container logs.

    See Also
    --------
    [`brightwebapp.brightway.load_and_set_useeio_project`][]
    ```
    """
    background_tasks.add_task(load_and_set_useeio_project)
    return {
        "status": "accepted",
        "message": "The USEEIO-1.1 database setup has been scheduled. This may take several minutes."
    }


@router.post("/traversal/perform", response_class=Response)
async def run_graph_traversal(request: GraphTraversalRequest):
    """
    Performs a graph traversal and returns the result as a CSV file.

    This endpoint serves as the primary calculation interface. It accepts a
    detailed JSON object specifying the demand, method, and calculation
    parameters. Upon success, it directly returns a CSV file for download.

    Parameters
    ----------
    request : GraphTraversalRequest
        A Pydantic model representing the structured request body. FastAPI
        automatically validates the incoming JSON against this model. See the
        documentation for the ``GraphTraversalRequest`` model for the exact
        JSON structure required.

    Returns
    -------
    fastapi.Response
        On success, a streaming response containing the graph traversal data
        as a CSV file. The HTTP ``Content-Disposition`` header is set to
        'attachment', prompting a file download in browsers.

    Raises
    ------
    HTTPException
        - **400 Bad Request**: Raised if the underlying calculation function
          returns a ``ValueError``. This can occur if, for example, the
          cutoff value is too high and no graph edges are found. The response
          body will contain the specific error message.
        - **500 Internal Server Error**: Raised for any other unexpected
          exception during processing, such as providing a demand ``code``
          that does not exist in the Brightway database.

    See Also
    --------
    [`brightwebapp.traversal.perform_graph_traversal`][]

    Example
    -------
    To trigger this endpoint, you must send a ``POST`` request with a JSON
    body. The following ``curl`` command demonstrates this.

    **Request:**

    ```bash
    curl -X POST http://localhost:8080/traversal/perform \\
    -H "Content-Type: application/json" \\
    -d '{
            "demand": [
            { "code": "some_valid_code", "amount": 1 }
            ],
            "method": ["IMPACT World+ Midpoint", "Climate change", "GWP100"],
            "cutoff": 0.005,
            "biosphere_cutoff": 1e-5,
            "max_calc": 10000
        }' \\
    --output traversal_result.csv
    ```
    On success, the command will be silent and the output will be saved to
    the file ``traversal_result.csv``.

    **Example Error Response (400 Bad Request):**

    ```json
    {
        "detail": "No edges found in the graph traversal. This may be due to a cutoff value that is too high, or a demand that does not lead to any edges."
    }
    ```
       
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
