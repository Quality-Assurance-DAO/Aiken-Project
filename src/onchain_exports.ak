// Re-export modules for on-chain validator entrypoints
use cardano/transaction.{Transaction}

pub use contract/datum.{DistributionContract}
pub use contract/redeemer.{ClaimRedeemer}
pub use contract/lib.{validate}

// Import test modules to ensure they're part of compilation graph
use tests

/// Helper to expose validator logic to .ak entrypoints
pub fn run_validator(
  datum: Option<DistributionContract>,
  redeemer: ClaimRedeemer,
  tx: Transaction
) -> Bool {
  let contract = when datum is {
    Some(d) -> d
    None -> return False
  }

  validate(contract, redeemer, tx)
}

