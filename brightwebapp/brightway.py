# %%
from typing import Optional
import bw2data as bd
import bw2io as bi


def load_and_set_ecoinvent_project(
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> None:
    """Checks if the ecoinvent 3.10 Brightway project is installed.
    If not, loads it from Ecoinvent servers using
    [`bw2io.bi.import_ecoinvent_release`](https://docs.brightway.dev/en/latest/content/api/bw2io/index.html#bw2io.import_ecoinvent_release)
    and installs it.
    """
    if "ei_3_10" not in bd.projects:
        if username is None or password is None:
            raise ValueError("Username and password must be provided to load ecoinvent project.")
        bi.import_ecoinvent_release(
            version='3.10',
            system_model='cutoff',
            username=username,
            password=password,
        )
    else:
        pass
    bd.projects.set_current(name='ei_3_10')


def load_and_set_useeio_project() -> None:
    """
    Checks if the USEEIO-1.1 Brightway project is installed.
    If not, loads it from Brightway servers and installs it.
    """
    if 'USEEIO-1.1' not in bd.projects:
        bi.install_project(project_key="USEEIO-1.1", overwrite_existing=True)
    else:
        pass
    bd.projects.set_current(name='USEEIO-1.1')