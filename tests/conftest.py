from typing import cast

import pytest

from trio_vis.trio_fake import FakeTrioTask, build_tree_from_json


@pytest.fixture
def fake_tree() -> FakeTrioTask:
    tmpl = {
        "name": "t1",
        "nurseries": [
            {
                "name": "n1",
                "tasks": [
                    {
                        "name": "t2",
                        "nurseries": [],
                    },
                    {
                        "name": "t3",
                        "nurseries": [],
                    },
                ],
            }
        ],
    }
    return cast(FakeTrioTask, build_tree_from_json(tmpl))
