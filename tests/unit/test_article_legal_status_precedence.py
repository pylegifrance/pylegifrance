"""Regression test for Article.from_orm's legal_status field precedence."""

from pylegifrance.models.code.models import Article


class TestArticleLegalStatusPrecedence:
    def test_legal_status_prefers_version_specific_legalstatus_over_item_level_etat(
        self,
    ):
        """Search responses flatten {**item, **extract}: item-level "etat" is
        the article's overall/global status (same across every historical
        version of that article number), while extract-level "legalStatus" is
        the true per-version status. When both are present -- the real shape
        CODE_ETAT search hits take -- the version-specific one must win, or
        every historical version of an in-force article reports the item's
        "etat" (e.g. all "VIGUEUR") and a VIGUEUR-only filter becomes a no-op.
        """
        article = Article.from_orm(
            {
                "id": "LEGIARTI1",
                "num": "787 B",
                "etat": "VIGUEUR",
                "legalStatus": "MODIFIE",
            }
        )
        assert article.legal_status == "MODIFIE"
