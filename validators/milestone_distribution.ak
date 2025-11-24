use ./onchain_exports.{DistributionContract, ClaimRedeemer, run_validator}

/// Primary spending validator entry point compiled by Aiken
validator milestone_distribution {
  spend(
    datum: Option<DistributionContract>,
    redeemer: ClaimRedeemer,
    _utxo: OutputReference,
    tx: Transaction
  ) {
    run_validator(datum, redeemer, tx)
  }
}

