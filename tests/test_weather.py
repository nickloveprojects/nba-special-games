from app import weather


H = {"time": ["2026-11-01T17:00", "2026-11-01T18:00", "2026-11-01T19:00"], "temperature_2m": [50.2, 47.6, 45],
     "wind_speed_10m": [9.4, 16.1, 12], "wind_gusts_10m": [20, 28, 22], "precipitation_probability": [10, 55, 30]}


def test_pick_nearest_hour():
    w = weather.pick(H, "2026-11-01T18:10:00+00:00")
    assert w == {"indoor": False, "temp": 48, "wind": 16, "gust": 28, "rain": 55}
    assert weather.label(w) == "48°F, wind 16 mph, 55% rain"


def test_missing_data_is_blank():
    assert weather.pick({}, "2026-11-01T18:00:00+00:00") is None
    assert weather.label(None) == "" and weather.label({"indoor": True}) == "Indoors"


def test_passing_factor():
    assert weather.passing_factor(None) == 1.0 and weather.passing_factor({"indoor": True}) == 1.0
    assert weather.passing_factor({"temp": 70, "wind": 3}) == 1.0
    assert weather.passing_factor({"temp": 70, "wind": 20}) == 0.88
    assert round(weather.passing_factor({"temp": 30, "wind": 20}), 3) == round(0.88 * 0.95, 3)


def test_full_report_helpers():
    assert weather.compass(0) == "N" and weather.compass(225) == "SW" and weather.compass(359) == "N" and weather.compass(None) == ""
    assert "projections trim" in weather.effects({"indoor": False, "wind": 20, "temp": 60, "rain": 0})[0]
    assert any("not factored" in x for x in weather.effects({"indoor": False, "wind": 3, "temp": 60, "rain": 80}))
    assert weather.effects({"indoor": True}) == [] and "No weather concerns" in weather.effects({"indoor": False, "wind": 3, "temp": 60, "rain": 5})[0]


def test_low_rain_chance_is_not_called_drizzle():
    assert weather.condition(51, 1, 10) == "Clear" and weather.condition(61, 10, 90) == "Overcast"
    assert weather.condition(61, 60, 90) == "Light rain" and weather.condition(0, 0, 0) == "Clear"
