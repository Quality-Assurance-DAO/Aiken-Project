// Helper module to expose shared validator logic to .ak entrypoints
use contract/datum.{DistributionContract}
use contract/redeemer.{ClaimRedeemer}
use contract/lib.{validate}
use aiken/transaction.{Transaction}

pub fn run_validator(
  datum: Option<DistributionContract>,
  redeemer: ClaimRedeemer,
  tx: Transaction
) -> Bool {
  let contract = when datum {
    Some(d) -> d
    None -> return False
  }

  validate(contract, redeemer, tx)
}
    }

    validate(contract, redeemer, tx)
  }
}
