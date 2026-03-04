from specflow8.io_markdown import upsert_feature_block


def test_feature_block_golden_snapshot():
    content = upsert_feature_block("", "F-001", "Golden Title", "### Body\n- item")
    expected = """<!-- specflow8:feature:F-001:start -->
## [F-001] Golden Title
### Body
- item
<!-- specflow8:feature:F-001:end -->
"""
    assert content == expected
