use contract/datum.{DistributionContract}
use contract/redeemer.{ClaimRedeemer}
use contract/lib.{validate}

/// Primary spending validator entry point compiled by Aiken
validator milestone_distribution {
  spend(
    datum: Option<DistributionContract>,
    redeemer: ClaimRedeemer,
    _utxo: OutputReference,
    tx: Transaction
  ) {
    when datum {
      Some(contract) -> validate(contract, redeemer, tx)
      None -> False
    }
  }
}

