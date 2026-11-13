def test_general_company_question_returns_scoped_documents_and_risks(client):
    response = client.post(
        "/api/reports",
        json={
            "company": "ABC",
            "question": "Analyze Company ABC, summarize key changes, identify risk signals, and recommend follow-up actions.",
            "confirm": True,
        },
    )
    report = response.json()
    assert report["status"] == "complete"
    assert "SQL-ABC-2026-06" in report["summary"]
    assert all(s["id"].startswith("DOC-ABC") for s in report["sources"] if s["kind"] == "document")
    assert {f["severity"] for f in report["risk_factors"]} == {"high", "medium"}
