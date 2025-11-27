// Main validator logic for milestone-based token distribution

use cardano/address.{Address}
use aiken/collection/list
use aiken/interval.{IntervalBoundType}
use cardano/transaction.{Transaction}
use validator_layer/datum.{DistributionContract, BeneficiaryAllocation}
use validator_layer/redeemer.{ClaimRedeemer}
use validator_layer/oracle.{count_valid_signatures}
use lib/validation.{validate_amount, validate_timestamp_passed}

/// Core validation logic shared between on-chain validator and tests
pub fn validate(
  datum: DistributionContract,
  redeemer: ClaimRedeemer,
  tx: Transaction
) -> Bool {
  when list.at(datum.beneficiary_allocations, redeemer.beneficiary_index) is {
    Some(allocation) -> {
      let unclaimed = !allocation.claimed
      let current_time =
        when tx.validity_range.lower_bound.bound_type is {
          IntervalBoundType.Finite(t) -> t
          _ -> 0
        }
      let has_vested = validate_timestamp_passed(allocation.vesting_timestamp, current_time)
      let milestone_matches =
        redeemer.milestone_verification.milestone_identifier == allocation.milestone_identifier
      let valid_count = count_valid_signatures(
        redeemer.milestone_verification.oracle_signatures,
        datum.oracle_addresses
      )
      let quorum_met = valid_count >= datum.quorum_threshold

      let outputs = tx.outputs
      let beneficiary_output = list.find(outputs, fn(output) {
        output.address == allocation.beneficiary_address
      })
      let has_beneficiary =
        when beneficiary_output is {
          Some(_output) -> True
          None -> False
        }

      (unclaimed && has_vested && milestone_matches && quorum_met && has_beneficiary)
    }
    None -> False
  }
}

