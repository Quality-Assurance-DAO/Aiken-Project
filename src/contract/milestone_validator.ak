use cardano/transaction.{Transaction, OutputReference}
use contract/datum.{DistributionContract}
use contract/redeemer.{ClaimRedeemer}
use contract/lib.{run_validator}

/// Primary milestone distribution validator entry point
validator milestone_distribution {
  spend(
    datum: Option<DistributionContract>,
    redeemer: ClaimRedeemer,
    _utxo: OutputReference,
    tx: Transaction
  ) -> Bool {
    run_validator(datum, redeemer, tx)
  }
}
