// Redeemer type definitions for claim transactions

use validator_layer/oracle.{OracleSignature}

/// Milestone verification data
pub type MilestoneVerification {
  milestone_identifier: ByteArray,
  oracle_signatures: List<OracleSignature>,
  verification_timestamp: Int,
}

/// Claim transaction redeemer
pub type ClaimRedeemer {
  beneficiary_index: Int,
  milestone_verification: MilestoneVerification,
}




