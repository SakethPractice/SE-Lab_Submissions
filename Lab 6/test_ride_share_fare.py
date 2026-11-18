import unittest

import pytest

from ride_share_fare import extra_distance_fare, pickup_status, seats_and_bags_ok


@pytest.mark.parametrize(
    ("cab_type", "distance_km", "zone", "is_subscriber", "expected"),
    [
        ("sedan", 5, "city", False, 0),  # At or below included distance.
        ("mini", 9, "city", True, 12),  # Subscriber allowance for non-SUV.
        ("suv", 13, "city", True, 12),  # SUV subscriber gets no extra allowance.
        ("sedan", 9, "suburb", False, 18),  # Non-city rate.
        ("mini", 26, "city", False, 420),  # City surcharge above 20 extra km.
        ("sedan", 29, "outstation", False, 630),  # Outstation surcharge above 20 km.
    ],
)
def test_extra_distance_fare(cab_type, distance_km, zone, is_subscriber, expected):
    assert extra_distance_fare(cab_type, distance_km, zone, is_subscriber) == expected


@pytest.mark.parametrize(
    ("cab_type", "distance_km", "message"),
    [
        ("limousine", 10, "unknown cab type"),
        ("mini", -1, "invalid distance"),
    ],
)
def test_extra_distance_fare_rejects_invalid_input(cab_type, distance_km, message):
    with pytest.raises(ValueError, match=message):
        extra_distance_fare(cab_type, distance_km, "city", False)


class TestSeatsAndBags(unittest.TestCase):
    def test_wheelchair_passenger_limit(self):
        self.assertTrue(seats_and_bags_ok(2, 5, True))
        self.assertFalse(seats_and_bags_ok(3, 0, True))

    def test_regular_passenger_and_bag_limits(self):
        self.assertTrue(seats_and_bags_ok(4, 2, False))
        self.assertFalse(seats_and_bags_ok(5, 0, False))
        self.assertFalse(seats_and_bags_ok(4, 3, False))


class TestPickupStatus(unittest.TestCase):
    def test_scheduled_airport_cutoff_and_outcomes(self):
        self.assertEqual(pickup_status(20, True, True), "on_time")
        self.assertEqual(pickup_status(19, True, True), "delayed")
        self.assertEqual(pickup_status(4, True, True), "missed")

    def test_unscheduled_non_airport_cutoff_and_outcomes(self):
        self.assertEqual(pickup_status(5, False, False), "on_time")
        self.assertEqual(pickup_status(4, False, False), "delayed")
        self.assertEqual(pickup_status(-11, False, False), "missed")
