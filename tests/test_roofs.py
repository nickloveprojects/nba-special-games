from app import roofs, weather


def test_roof_types():
    assert roofs.roof_for("Ford Field", True) == "fixed"
    assert roofs.roof_for("Caesars Superdome", True) == "fixed"
    assert roofs.roof_for("Allegiant Stadium", True) == "fixed"
    for name in ("State Farm Stadium", "Mercedes-Benz Stadium", "AT&T Stadium", "NRG Stadium", "Lucas Oil Stadium"):
        assert roofs.roof_for(name, True) == "retractable"
    assert roofs.roof_for("SoFi Stadium", False) == "canopy"
    assert roofs.roof_for("Lambeau Field", False) == "open"
    assert roofs.roof_for("Some New Dome", True) == "retractable"   # unknown indoor venue is never trusted as enclosed


def test_retractable_never_scored_or_adjusted():
    g = [{"id": "a", "lat": 33.5, "lon": -112.2, "tip_utc": "2026-11-15T18:00:00+00:00", "indoor": True, "roof": "retractable"}]
    out = weather.forecast_many(g)["a"]
    assert out["indoor"] and weather.passing_factor(out) == 1.0
    assert "unknown" in weather.label(out)
    assert weather.label({"indoor": True, "roof": "fixed"}) == "Indoors"
