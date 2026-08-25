from annotate.sampling import stratified_sample


def test_stratified_sample_sums_to_target():
    counts = {"myjoyonline": 155, "graphic": 35, "citinewsroom": 155, "gna": 155, "ghpage": 167, "zionfelix": 167, "yen": 166}
    result = stratified_sample(counts, 250)
    assert sum(result.values()) == 250


def test_stratified_sample_matches_expected_allocation():
    counts = {"myjoyonline": 155, "graphic": 35, "citinewsroom": 155, "gna": 155, "ghpage": 167, "zionfelix": 167, "yen": 166}
    result = stratified_sample(counts, 250)
    assert result == {
        "myjoyonline": 39,
        "graphic": 9,
        "citinewsroom": 39,
        "gna": 39,
        "ghpage": 42,
        "zionfelix": 41,
        "yen": 41,
    }


def test_stratified_sample_gives_every_nonzero_outlet_at_least_one():
    counts = {"a": 1, "b": 999}
    result = stratified_sample(counts, 10)
    assert sum(result.values()) == 10
    assert result["a"] >= 1
    assert result["b"] >= 1


def test_stratified_sample_simple_even_split():
    counts = {"a": 50, "b": 50}
    result = stratified_sample(counts, 10)
    assert result == {"a": 5, "b": 5}
