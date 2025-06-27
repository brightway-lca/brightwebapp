import pytest
import bw2io as bi
import bw2data as bd
from brightwebapp import brightway

def test_load_and_set_useeio_project():
    """
    Test the loading and setting of the USEEIO project.
    This function should ensure that the USEEIO-1.1 project is installed
    and set as the current project in Brightway.
    """
    # Ensure the USEEIO-1.1 project is not already loaded
    if "USEEIO-1.1" in bd.projects:
        bd.projects.delete_project(name='USEEIO-1.1', delete_dir=True)

    brightway.load_and_set_useeio_project()

    assert bd.projects.current == "USEEIO-1.1"
    assert "USEEIO-1.1" in bd.projects