"""
Tests automatiques — DevSecOps Demo App
Lancement : pytest tests/ --cov=app
"""


class TestHomePage:

    def test_home_returns_200(self, client):
        res = client.get("/")
        assert res.status_code == 200

    def test_home_contains_title(self, client):
        res = client.get("/")
        assert b"DevSecOps" in res.data

    def test_home_has_login_link(self, client):
        res = client.get("/")
        assert b"login" in res.data.lower()


class TestLoginPage:

    def test_login_page_returns_200(self, client):
        res = client.get("/login")
        assert res.status_code == 200

    def test_login_page_has_form(self, client):
        res = client.get("/login")
        assert b"<form" in res.data

    def test_login_success_redirects(self, client):
        """Un login correct doit rediriger vers le dashboard (302)."""
        res = client.post("/login", data={
            "username": "admin",
            "password": "admin123"
        })
        assert res.status_code == 302
        assert "/dashboard" in res.headers["Location"]

    def test_login_wrong_password_fails(self, client):
        """Un mauvais mot de passe doit afficher une erreur."""
        res = client.post("/login", data={
            "username": "admin",
            "password": "mauvais"
        })
        assert res.status_code == 200
        assert "incorrect" in res.data.decode().lower()

    def test_login_unknown_user_fails(self, client):
        res = client.post("/login", data={
            "username": "hacker",
            "password": "password"
        })
        assert res.status_code == 200
        assert "incorrect" in res.data.decode().lower()

    def test_login_empty_fields_fails(self, client):
        res = client.post("/login", data={"username": "", "password": ""})
        assert res.status_code in [200, 400]


class TestDashboard:

    def test_dashboard_without_login_redirects(self, client):
        """Dashboard sans login → redirect vers /login."""
        res = client.get("/dashboard")
        assert res.status_code == 302
        assert "login" in res.headers["Location"]

    def test_dashboard_with_login_returns_200(self, logged_in_client):
        res = logged_in_client.get("/dashboard")
        assert res.status_code == 200

    def test_dashboard_shows_username(self, logged_in_client):
        res = logged_in_client.get("/dashboard")
        assert b"admin" in res.data


class TestLogout:

    def test_logout_redirects_home(self, logged_in_client):
        res = logged_in_client.get("/logout")
        assert res.status_code == 302

    def test_after_logout_dashboard_blocked(self, logged_in_client):
        logged_in_client.get("/logout")
        res = logged_in_client.get("/dashboard")
        assert res.status_code == 302
        assert "login" in res.headers["Location"]


class TestAPI:

    def test_api_status_returns_200(self, client):
        res = client.get("/api/status")
        assert res.status_code == 200

    def test_api_status_returns_json(self, client):
        res = client.get("/api/status")
        data = res.get_json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_api_whoami_without_login_blocked(self, client):
        res = client.get("/api/whoami")
        assert res.status_code == 302

    def test_api_whoami_with_login_returns_user(self, logged_in_client):
        res = logged_in_client.get("/api/whoami")
        assert res.status_code == 200
        data = res.get_json()
        assert data["username"] == "admin"
        assert data["logged_in"] is True


class TestSecurity:

    def test_unknown_route_returns_404(self, client):
        res = client.get("/cette-page-nexiste-pas-xyz")
        assert res.status_code == 404

    def test_password_not_in_response(self, client):
        """Le mot de passe ne doit JAMAIS apparaître dans une réponse."""
        res = client.post("/login", data={
            "username": "admin", "password": "admin123"
        }, follow_redirects=True)
        assert b"admin123" not in res.data

    def test_session_cleared_after_logout(self, logged_in_client):
        with logged_in_client.session_transaction() as sess:
            assert "username" in sess
        logged_in_client.get("/logout")
        with logged_in_client.session_transaction() as sess:
            assert "username" not in sess
