use cardano/transaction.{Transaction, OutputReference}
use contract/datum.{DistributionContract}
use contract/redeemer.{ClaimRedeemer}
use contract/lib.{run_validator}

validator simple {
  spend(
    datum: Option<DistributionContract>,
    redeemer: ClaimRedeemer,
    _utxo: OutputReference,
    tx: Transaction
  ) {
    run_validator(datum, redeemer, tx)
  }
}

