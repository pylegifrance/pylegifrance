# ruff: noqa: F403
from pytest_bdd import scenarios

from tests.integration.fonds.loda.steps import *
from tests.integration.fonds.shared import *

scenarios("loda.feature")
