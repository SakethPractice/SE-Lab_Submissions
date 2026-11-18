import math

from hypothesis import given, strategies as st

from ride_share_fare import fare_average, parse_trip, payable_fare


unexpected_values = st.one_of(
    st.text(),
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(allow_nan=True, allow_infinity=True),
    st.binary(),
    st.lists(st.text()),
    st.dictionaries(st.text(), st.text()),
)


@given(value=unexpected_values)
def test_parse_trip_handles_unexpected_inputs(value):
    result = parse_trip(value)
    assert result is None or (
        isinstance(result, tuple)
        and len(result) == 2
        and isinstance(result[0], str)
        and bool(result[0].strip())
        and isinstance(result[1], float)
        and math.isfinite(result[1])
        and result[1] >= 0
    )


@given(value=unexpected_values)
def test_fare_average_handles_unexpected_inputs(value):
    result = fare_average(value)
    assert result is None or (isinstance(result, int) and result >= 0)


@given(value=unexpected_values)
def test_payable_fare_handles_unexpected_inputs(value):
    result = payable_fare(value)
    assert result is None or (
        isinstance(result, float) and math.isfinite(result) and result >= 0
    )


@given(
    cab=st.sampled_from(["mini", "sedan", "suv"]),
    distance=st.floats(
        min_value=0, max_value=1_000_000, allow_nan=False, allow_infinity=False
    ),
)
def test_parse_trip_preserves_valid_inputs(cab, distance):
    parsed_cab, parsed_distance = parse_trip(f"{cab}:{distance}")
    assert parsed_cab == cab.title()
    assert parsed_distance == distance


@given(fares=st.lists(st.integers(min_value=0, max_value=1_000_000), min_size=1))
def test_fare_average_preserves_valid_inputs(fares):
    fares_csv = ",".join(str(fare) for fare in fares)
    assert fare_average(fares_csv) == sum(fares) // len(fares)


@given(
    fare=st.integers(min_value=0, max_value=1_000_000),
    promo=st.integers(min_value=0, max_value=1_000_000),
)
def test_payable_fare_preserves_valid_inputs(fare, promo):
    assert payable_fare(f"{fare}|{promo}") == max(fare * 1.18 - promo, 0)
