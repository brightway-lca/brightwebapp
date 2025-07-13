from typing import Optional
import bw2data as bd
import bw2io as bi
import os

def load_and_set_ecoinvent_project(
    username: Optional[str] = None,
    password: Optional[str] = None,
    overwrite_existing: bool = False
) -> None:
    """Checks if the ecoinvent 3.10 Brightway project is installed.
    If not, loads it from Ecoinvent servers and installs it.

    Notes
    -----
    `username` and `password` are required to access the Ecoinvent database.

    See Also
    --------
    [`bw2io.bi.import_ecoinvent_release`](https://docs.brightway.dev/en/latest/content/api/bw2io/index.html#bw2io.import_ecoinvent_release)
    """
    project_name = 'ei_3_10'

    # 1. if overwrite is requested, delete the project if it exists.
    if overwrite_existing and project_name in bd.projects:
        bd.projects.delete_project(project_name, delete_dir=True)

    # 2. if the project doesn't exist, import it.
    if project_name not in bd.projects:
        if not username or not password:
            raise ValueError("Username and password are required to download the ecoinvent database.")
        bi.import_ecoinvent_release(
            version='3.10',
            system_model='cutoff',
            username=username,
            password=password,
        )

    # 3. now that the project is guaranteed to exist, set it as current.
    bd.projects.set_current(project_name)

    return 


def load_and_set_useeio_project() -> None:
    """
    Checks if the USEEIO-1.1 Brightway project is installed.
    If not, loads it from Brightway servers and installs it.

    See Also
    --------
    [`bw2io.remote.install_project`](https://docs.brightway.dev/en/latest/content/api/bw2io/remote/index.html#bw2io.remote.install_project)

    Notes
    -----
    The USEEIO-1.1 project is also available from the Brightway data repository at:
    
    ```
    https://files.brightway.dev/USEEIO-1.1.tar.gz
    ```

    However, this function loads it from a GitHub repository, which is more reliable and has guaranteed uptime:

    Warnings
    --------
    The Zenodo URL where this file is archived
    
    ```
    https://zenodo.org/records/15685370/files/USEEIOv1.1.tar.gz
    ```
    
    cannot be used directly due to browser CORS (Cross-Origin Resource Sharing)
    security policies. The Zenodo link redirects to a file server
    that lacks the required CORS headers, causing the browser
    to block the download. This function therefore uses a copy
    hosted on raw.githubusercontent.com, which is correctly
    configured for cross-origin access.
    """
    if 'USEEIO-1.1' not in bd.projects:
        bi.install_project(
        project_key="USEEIO-1.1",
        project_name="USEEIO-1.1",
        projects_config={"USEEIO-1.1": "USEEIOv1.1.tar.gz"},
        url="https://raw.githubusercontent.com/brightway-lca/brightwebapp/main/data/",
        overwrite_existing=True
    )
    else:
        pass
    bd.projects.set_current(name='USEEIO-1.1')


def brightway_wasm_database_storage_workaround() -> None:
    """
    Sets the Brightway project directory to `/tmp/.
    
    The JupyterLite file system currently does not support storage of SQL database files
    in directories other than `/tmp/`. This function sets the Brightway environment variable
    `BRIGHTWAY_DIR` to `/tmp/` to work around this limitation.
    
    See Also
    --------
    - [Brightway Documentation: "How do I change my Data Directory"?](https://docs.brightway.dev/en/latest/content/faq/data_management.html#how-do-i-change-my-data-directory)
    - [Brightway Live Issue #10](https://github.com/brightway-lca/brightway-live/issues/10)
    """
    os.environ["BRIGHTWAY_DIR"] = "/tmp/"