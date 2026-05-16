import pytest

from labmm.models.lab_membership import LabRole


def test_lab_role_has_four_values():
    assert len(LabRole) == 4


def test_lab_role_values():
    values = {r.value for r in LabRole}
    assert values == {"manager", "engineer", "researcher", "staff"}


def test_lab_role_from_string():
    assert LabRole("manager") == LabRole.manager
    assert LabRole("staff") == LabRole.staff


def test_lab_role_invalid_raises():
    with pytest.raises(ValueError):
        LabRole("superstar")
