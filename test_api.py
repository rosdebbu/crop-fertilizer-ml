from fastapi.testclient import TestClient
import app as m

c = TestClient(m.app)
CROP = dict(N=90, P=42, K=43, temperature=21, humidity=82, ph=6.5, rainfall=203)

def test_crop_prediction_is_rice():
    r = c.post("/api/predict/crop", json=CROP).json()
    assert r["crop"] == "rice" and set(r["multi_model_comparison"]) == {"Random Forest", "Decision Tree", "KNN"}

def test_crop_rejects_out_of_range():
    assert c.post("/api/predict/crop", json={**CROP, "ph": 99}).status_code == 422

def test_fertilizer_bad_soil_is_400():
    body = dict(Temperature=30, Humidity=50, Moisture=40, Soil_Type="Nope",
                Nitrogen=10, Phosphorous=10, Potassium=10)
    assert c.post("/api/predict/fertilizer", json=body).status_code == 400

def test_status_reports_data_quality():
    q = c.get("/api/status").json()["data_quality"]
    assert q["crop"]["warning"] is None and q["crop"]["best_accuracy_pct"] > 90

def test_fertilizer_quality_flag_is_honest():
    q = c.get("/api/status").json()["data_quality"]["fertilizer"]
    assert (q["warning"] is None) == (q["best_accuracy_pct"] >= q["chance_level_pct"] + 10)

def test_pipeline_learns_when_labels_have_signal():
    import importlib.util, pathlib
    spec = importlib.util.spec_from_file_location("mk", pathlib.Path(__file__).parent / "scripts" / "make_fertilizer_dataset.py")
    mk = importlib.util.module_from_spec(spec); spec.loader.exec_module(mk)
    d = mk.build(2000)
    X = d[["Temperature", "Humidity", "Moisture", "Nitrogen", "Phosphorous", "Potassium"]]
    *_, quality = m.fit_and_score(X, d["Fertilizer Name"])
    assert quality["warning"] is None and quality["best_accuracy_pct"] > 80
