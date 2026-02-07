from __future__ import annotations

import pytest
from pytest_examples import CodeExample, EvalExample, find_examples


@pytest.mark.parametrize("example", find_examples("README.md"), ids=str)
def test_readme(example: CodeExample, eval_example: EvalExample) -> None:
    eval_example.config.line_length = 120
    eval_example.config.target_version = "py310"
    eval_example.config.magic_trailing_comma = False
    eval_example.config.ruff_ignore = ["F704", "F821"]
    if eval_example.update_examples:
        eval_example.format(example)
    else:
        eval_example.lint(example)
