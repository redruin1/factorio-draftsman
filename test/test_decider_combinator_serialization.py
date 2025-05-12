import pytest
from draftsman.blueprintable import Blueprint
from draftsman.entity import DeciderCombinator
from draftsman.constants import Direction

@pytest.mark.parametrize("direction", [Direction.EAST])
def test_decider_combinator_conditions_and_outputs(direction):
    blueprint = Blueprint()
    dc = DeciderCombinator("decider-combinator", direction=direction)
    Input = DeciderCombinator.Input
    Output = DeciderCombinator.Output
    dc.conditions = (
        (Input("signal-A") > Input("signal-B", {"red"}))
        & (Input("signal-C", {"green"}) == Input("signal-D"))
        | (Input("signal-each", {"green"}) <= Input("signal-each", {"red", "green"}))
    )
    dc.conditions |= (Input("transport-belt", networks={"green"}) != -2**31)
    dc.outputs = [
        Output("signal-A", copy_count_from_input=False),
        Output("signal-each", networks={"green"}),
        Output("signal-B", copy_count_from_input=False, constant=101)
    ]
    blueprint.entities.append(dc)
    exported = blueprint.to_string()
    print("\n--- SERIALIZED BLUEPRINT STRING ---\n", exported, "\n--- END ---\n")
    imported = Blueprint(exported)
    # Find the decider combinator entity
    imported_dc = None
    for ent in imported.entities:
        if isinstance(ent, DeciderCombinator):
            imported_dc = ent
            break
    assert imported_dc is not None, "DeciderCombinator not found after import"
    # Check that conditions and outputs are present and non-empty
    assert hasattr(imported_dc, "conditions"), "No 'conditions' attribute after import"
    print("Imported DeciderCombinator conditions:", imported_dc.conditions)
    assert imported_dc.conditions, "Conditions list is empty after import"
    assert hasattr(imported_dc, "outputs"), "No 'outputs' attribute after import"
    print("Imported DeciderCombinator outputs:", imported_dc.outputs)
    assert imported_dc.outputs, "Outputs list is empty after import"
    # Optionally: check specific signals or structure
    signals = [getattr(c, 'first_signal', None) for c in imported_dc.conditions]
    assert any(s is not None for s in signals), "No signals found in imported conditions"
