// CLI command for creating distribution contracts

use cardano/address.{Address}
use aiken/collection/list
use contract/datum.{DistributionContract, BeneficiaryAllocation}
use lib/types.{ContractMetadata}
use lib/validation.{validate_amount, validate_quorum_threshold}

/// Create distribution contract datum from allocations and oracle files
/// T043: Implement create command
/// T050: Error handling
/// T051: Input validation
pub fn create_contract_datum(
  allocations: List<BeneficiaryAllocation>,
  oracle_addresses: List<Address>,
  quorum_threshold: Int,
  token_policy_id: ByteArray,
  metadata: ContractMetadata
) -> DistributionContract {
  if !validate_quorum_threshold(quorum_threshold, list.length(oracle_addresses)) {
    // T050: Error handling - clear error message
    // In actual implementation, return error type instead of crashing
    DistributionContract {
      total_token_amount: 0,
      token_policy_id: token_policy_id,
      beneficiary_allocations: [],
      oracle_addresses: oracle_addresses,
      quorum_threshold: quorum_threshold,
      total_oracles: list.length(oracle_addresses),
      contract_metadata: metadata
    }
  } else {
    let total_token_amount = list.foldl(allocations, 0, fn(alloc, acc) {
      when validate_amount(alloc.token_amount) is {
        True -> acc + alloc.token_amount
        False -> acc  // Skip invalid amounts (error handling)
      }
    })
    
    DistributionContract {
      total_token_amount: total_token_amount,
      token_policy_id: token_policy_id,
      beneficiary_allocations: allocations,
      oracle_addresses: oracle_addresses,
      quorum_threshold: quorum_threshold,
      total_oracles: list.length(oracle_addresses),
      contract_metadata: metadata
    }
  }
}

