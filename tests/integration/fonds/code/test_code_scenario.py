# ruff: noqa: F403
from tests.integration.fonds.code.steps import *
from tests.integration.fonds.shared import *
from pytest_bdd import scenarios

scenarios("code.feature")
