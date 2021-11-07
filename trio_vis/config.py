from pathlib import Path

from pydantic import BaseModel, validator


class VisConfig(BaseModel):

    # Ignore trio's internal nursery/task
    # the side effect is that we would inspect every task/nersery's code object
    # so we would like to disable this config while testing
    only_vis_user_scope: bool = True

    print_task_tree: bool = True

    log_overwrite_if_exists: bool = True
    log_filename: str = "./sc-logs.json"

    @validator("log_filename")
    def log_file_should_not_be_overwritten_unless_required(cls, filename: str, values):
        if Path(filename).exists() and values["log_overwrite_if_exists"] is False:
            raise ValueError(
                f"[trio-vis] file exists with overwrite set to false:{filename}"
            )
        return filename
