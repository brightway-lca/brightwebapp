from fastapi import APIRouter, Response, BackgroundTasks, HTTPException
from io import StringIO
from pydantic import BaseModel


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
    Schedules a background task to download and install the USEEIO-1.1
    database if it is not already present.

    See Also
    --------
    [`brightwebapp.brightway.load_and_set_useeio_project`][]
    """
    background_tasks.add_task(load_and_set_useeio_project)
    return {
        "status": "accepted",
        "message": "The USEEIO-1.1 database setup has been scheduled. This may take several minutes."
    }


@router.post("/traversal/perform", response_class=Response)
async def run_graph_traversal(request: GraphTraversalRequest):
    """
    Performs a graph traversal based on a detailed request body
    and returns the resulting graph as a CSV file.

    See Also
    --------
    [`brightwebapp.traversal.perform_graph_traversal`][]
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
