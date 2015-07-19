
def test_dotted_lower():
    from env2config.conversions import dotted_lower

    given = 'FOO_BAR'
    expected = 'foo.bar'
    result = dotted_lower(given)

    assert result == expected


def test_dotted_lower_trailing():
    from env2config.conversions import dotted_lower

    given = 'FOO_BAR_'
    expected = 'foo.bar.'
    result = dotted_lower(given)

    assert result == expected


def test_dashed_lower():
    from env2config.conversions import dashed_lower

    given = 'FOO_BAR'
    expected = 'foo-bar'
    result = dashed_lower(given)

    assert result == expected


def test_dashed_lower_trailing():
    from env2config.conversions import dashed_lower

    given = 'FOO_BAR_'
    expected = 'foo-bar-'
    result = dashed_lower(given)

    assert result == expected

