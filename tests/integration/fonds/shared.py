from pytest_bdd import given


@given("l'API Légifrance est accessible")
def api_legifrance_accessible(api_client):
    """Vérifie que l'API Légifrance est accessible via ping."""
    success = api_client.ping()
    assert success is True, "L'API Légifrance doit être accessible (ping failed)"


@given("un client API est configuré")
def client_api_configure_existing(api_client):
    """Utilise le client API existant."""
    assert api_client is not None, "Le client API doit être disponible"
