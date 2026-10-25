"""Runs every scenario of the specification's feature files."""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.bdt

scenarios("../../specification/acceptance")
