// Datum type definitions for the milestone token distribution validator

use cardano/address.{Address}
use lib/types.{ContractMetadata}

/// Beneficiary allocation record
pub type BeneficiaryAllocation {
  beneficiary_address: Address,
  token_amount: Int,
  milestone_identifier: ByteArray,
  vesting_timestamp: Int,
  claimed: Bool,
}

/// Distribution contract datum
pub type DistributionContract {
  total_token_amount: Int,
  token_policy_id: ByteArray,
  beneficiary_allocations: List<BeneficiaryAllocation>,
  oracle_addresses: List<Address>,
  quorum_threshold: Int,
  total_oracles: Int,
  contract_metadata: ContractMetadata,
}




