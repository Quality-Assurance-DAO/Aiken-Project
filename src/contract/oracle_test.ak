// Unit tests for oracle signature verification logic

use cardano/address.{Address, from_verification_key}
use aiken/crypto.{blake2b_224}
use aiken/collection/list
use contract/oracle.{OracleSignature, remove_duplicate_oracles, count_valid_signatures}

fn mk_address(tag: ByteArray) -> Address {
  from_verification_key(blake2b_224(tag))
}

// T028: Unit test for valid quorum acceptance
test valid_quorum_acceptance() {
  // Create test oracle signatures
  let sig1 = OracleSignature {
    oracle_address: mk_address(#"01"),
    signature_hash: #"aa",
    signed_data: #"deadbeef",
    signature_timestamp: 1735689600
  }
  
  let sig2 = OracleSignature {
    oracle_address: mk_address(#"02"),
    signature_hash: #"bb",
    signed_data: #"deadbeef",
    signature_timestamp: 1735689600
  }
  
  let sig3 = OracleSignature {
    oracle_address: mk_address(#"03"),
    signature_hash: #"cc",
    signed_data: #"deadbeef",
    signature_timestamp: 1735689600
  }
  
  let signatures = [sig1, sig2, sig3]
  let authorized = [
    mk_address(#"01"),
    mk_address(#"02"),
    mk_address(#"03"),
    mk_address(#"04"),
    mk_address(#"05"),
  ]
  
  // Test quorum threshold of 3 with 3 valid signatures
  let count = count_valid_signatures(signatures, authorized)
  count >= 3
}

// T029: Unit test for quorum failure rejection
test quorum_failure_rejection() {
  // Create test oracle signatures (only 2, need 3)
  let sig1 = OracleSignature {
    oracle_address: mk_address(#"01"),
    signature_hash: #"aa",
    signed_data: #"deadbeef",
    signature_timestamp: 1735689600
  }
  
  let sig2 = OracleSignature {
    oracle_address: mk_address(#"02"),
    signature_hash: #"bb",
    signed_data: #"deadbeef",
    signature_timestamp: 1735689600
  }
  
  let signatures = [sig1, sig2]
  let authorized = [
    mk_address(#"01"),
    mk_address(#"02"),
    mk_address(#"03"),
    mk_address(#"04"),
    mk_address(#"05"),
  ]
  
  // Test quorum threshold of 3 with only 2 valid signatures
  let count = count_valid_signatures(signatures, authorized)
  count < 3
}

// T030: Unit test for duplicate signature handling
test duplicate_signature_handling() {
  // Create duplicate signatures from same oracle
  let sig1 = OracleSignature {
    oracle_address: mk_address(#"01"),
    signature_hash: #"aa",
    signed_data: #"deadbeef",
    signature_timestamp: 1735689600
  }
  
  let sig2 = OracleSignature {
    oracle_address: mk_address(#"01"),  // Same oracle
    signature_hash: #"bb",
    signed_data: #"deadbeef",
    signature_timestamp: 1735689700
  }
  
  let sig3 = OracleSignature {
    oracle_address: mk_address(#"02"),
    signature_hash: #"cc",
    signed_data: #"deadbeef",
    signature_timestamp: 1735689600
  }
  
  let signatures = [sig1, sig2, sig3]
  
  // After deduplication, should count only 2 unique oracles
  let unique = remove_duplicate_oracles(signatures)
  list.length(unique) == 2
}

