# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean CLI v1.0. Copyright 2021 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional

import click

from lean.click import LeanCommand
from lean.container import container


@click.command(cls=LeanCommand)
@click.option("--project", type=str, help="Name or id of the project to pull (all cloud projects if not specified)")
@click.option("--pull-bootcamp", is_flag=True, default=False, help="Pull Boot Camp projects (disabled by default)")
def pull(project: Optional[str], pull_bootcamp: bool) -> None:
    """Pull projects from QuantConnect to the local drive.

    This command overrides the content of local files with the content of their respective counterparts in the cloud.

    This command will not delete local files for which there is no counterpart in the cloud.
    """
    # Parse which projects need to be pulled
    project_id = None
    if project is not None:
        try:
            project_id = int(project)
        except ValueError:
            pass

    api_client = container.api_client()
    all_projects = api_client.projects.get_all()
    project_manager = container.project_manager()
    projects_to_pull = project_manager.get_projects_by_name_or_id(all_projects, project_id or project)

    if project is None and not pull_bootcamp:
        projects_to_pull = [p for p in projects_to_pull if not p.name.startswith("Boot Camp/")]

    pull_manager = container.pull_manager()
    pull_manager.pull_projects(projects_to_pull, all_projects)
