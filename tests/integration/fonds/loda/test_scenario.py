# ruff: noqa: F403
from tests.integration.fonds.loda.steps import *
from tests.integration.fonds.shared import *
from pytest_bdd import scenarios

scenarios("loda.feature")
