from specflow8.io_markdown import (
    MANUAL_END,
    MANUAL_START,
    extract_feature_block,
    upsert_feature_block,
)


def test_upsert_feature_block_is_idempotent_and_preserves_manual():
    content = ""
    body = "### Body\n- value"
    content = upsert_feature_block(content, "F-001", "Title", body)
    assert "<!-- specflow8:feature:F-001:start -->" in content

    original = extract_feature_block(content, "F-001")
    assert original is not None
    with_manual = (
        original
        + "\n\n"
        + MANUAL_START
        + "\nmanual keep\n"
        + MANUAL_END
    )
    content = upsert_feature_block(content, "F-001", "Title", with_manual)
    content = upsert_feature_block(content, "F-001", "Title", "### Body\n- changed")
    updated = extract_feature_block(content, "F-001")
    assert updated is not None
    assert "manual keep" in updated
