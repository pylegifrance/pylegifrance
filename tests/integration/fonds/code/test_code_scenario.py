# ruff: noqa: F403
from pytest_bdd import scenarios

from tests.integration.fonds.code.steps import *
from tests.integration.fonds.shared import *

scenarios("code.feature")
