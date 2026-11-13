def test_vertical_slice(client):
    overview = client.get("/api/overview").json()
    assert len(overview["companies"]) == 6
    req = {
        "company": "ABC",
        "question": "Analyze receivables aging and distributor settlement changes.",
        "confirm": True,
    }
    response = client.post("/api/reports", json=req)
    assert response.status_code == 201, response.text
    report = response.json()
    assert report["status"] == "complete", report["steps"]
    assert report["usage"]["cost_usd"] == 0
    assert {f["citation"] for f in report["findings"]} <= {s["id"] for s in report["sources"]}
    assert len(report["steps"]) == 5
    assert client.get("/api/overview").json()["reports"] == 1
