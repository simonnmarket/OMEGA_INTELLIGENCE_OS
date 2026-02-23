//+------------------------------------------------------------------+
//| CryptoSecurityExample.mq5 - Institutional Security Demo          |
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Labs - Confidential"
#property strict

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() {
    // Verify institutional compliance
    if(!InstitutionalCrypto::MeetsInstitutionalStandards()) {
        Print("WARNING: System does not meet institutional security standards!");
        return INIT_FAILED;
    }
    
    // Test various hash algorithms
    TestHashAlgorithms();
    
    // Test quantum-resistant features
    TestQuantumSecurity();
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Test different hash algorithms                                   |
//+------------------------------------------------------------------+
void TestHashAlgorithms() {
    string testData = "Institutional Trading Data";
    uchar hash[64];
    
    // Test SHA-256
    if(InstitutionalCrypto::HashData(CRYPT_HASH_SHA256, testData, hash)) {
        Print("SHA-256 Hash: ", BytesToHex(hash));
    }
    
    // Test SHA-512
    if(InstitutionalCrypto::HashData(CRYPT_HASH_SHA512, testData, hash)) {
        Print("SHA-512 Hash: ", BytesToHex(hash));
    }
    
    // Test SHA3-256
    if(InstitutionalCrypto::HashData(CRYPT_HASH_SHA3_256, testData, hash)) {
        Print("SHA3-256 Hash: ", BytesToHex(hash));
    }
    
    // Test BLAKE2s
    if(InstitutionalCrypto::HashData(CRYPT_HASH_BLAKE2s, testData, hash)) {
        Print("BLAKE2s Hash: ", BytesToHex(hash));
    }
}

//+------------------------------------------------------------------+
//| Test quantum-resistant features                                  |
//+------------------------------------------------------------------+
void TestQuantumSecurity() {
    string testData = "Quantum-Resistant Data";
    uchar hash[64];
    
    // Test XMSS
    if(InstitutionalCrypto::HashData(CRYPT_HASH_XMSS, testData, hash)) {
        Print("XMSS Hash: ", BytesToHex(hash));
    }
    
    // Test Dilithium verification
    uchar signature[64];
    if(CQuantumSecurity::Dilithium_Verify(signature)) {
        Print("Dilithium verification successful");
    }
}

//+------------------------------------------------------------------+
//| Utility function to convert bytes to hex string                  |
//+------------------------------------------------------------------+
string BytesToHex(const uchar &bytes[]) {
    string hex = "";
    for(int i = 0; i < ArraySize(bytes); i++) {
        hex += StringFormat("%02X", bytes[i]);
    }
    return hex;
} 