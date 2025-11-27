// Shared type definitions for the milestone token distribution system
// Note: Aiken has built-in types (Address, ByteArray, Int, Bool, List, Option)
// These are re-exported here for clarity, but can be used directly from aiken/builtin

use cardano/address.{Address}

/// Contract metadata type
pub type ContractMetadata {
  creation_timestamp: Int,
  creator_address: Address,
  contract_version: ByteArray,
  description: Option<ByteArray>,
}

