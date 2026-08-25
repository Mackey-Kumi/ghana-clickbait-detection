def stratified_sample(outlet_counts, target_total):
    outlets = [o for o, c in outlet_counts.items() if c > 0]
    total_available = sum(outlet_counts[o] for o in outlets)

    sizes = {o: 1 for o in outlets}
    remaining = target_total - len(outlets)

    raw_shares = {o: outlet_counts[o] * remaining / total_available for o in outlets}
    for o in outlets:
        sizes[o] += int(raw_shares[o])

    shortfall = target_total - sum(sizes.values())
    remainders = sorted(
        outlets,
        key=lambda o: raw_shares[o] - int(raw_shares[o]),
        reverse=True,
    )
    for o in remainders[:shortfall]:
        sizes[o] += 1

    return sizes
