// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DocumentVerify {

    address public admin;

    constructor() {
        admin = msg.sender;
    }

    struct Document {
        string docHash;
        string qrCodeData;
        uint256 timestamp;
    }

    mapping(string => Document) private documents;
    mapping(string => bool) private exists;

    event DocumentStored(
        string indexed passportNumber,
        string docHash,
        string qrCodeData,
        uint256 timestamp
    );

    /// @notice Admin uploads a verified document’s BLAKE3 hash and QR metadata
    function storeDocument(
        string memory passportNumber,
        string memory docHash,
        string memory qrCodeData
    ) public {
        require(msg.sender == admin, "Only admin can store");
        require(!exists[passportNumber], "Already stored");
        require(bytes(passportNumber).length > 0, "Passport required");
        require(bytes(docHash).length > 0, "Hash required");

        documents[passportNumber] = Document({
            docHash: docHash,
            qrCodeData: qrCodeData,
            timestamp: block.timestamp
        });

        exists[passportNumber] = true;

        emit DocumentStored(passportNumber, docHash, qrCodeData, block.timestamp);
    }

    /// @notice Verify if passportNumber and BLAKE3 hash match what's stored
    /// @param passportNumber The document identifier
    /// @param inputHash The BLAKE3 hash of the document submitted by user
    /// @return isValid Returns true if hash matches
    function verifyDocument(
        string memory passportNumber,
        string memory inputHash
    ) public view returns (bool isValid) {
        require(exists[passportNumber], "Document not found");
        Document memory doc = documents[passportNumber];
        return (keccak256(abi.encodePacked(doc.docHash)) == keccak256(abi.encodePacked(inputHash)));
    }

    /// @notice Optional: View document QR metadata
    function getQRCodeData(string memory passportNumber) public view returns (string memory) {
        require(exists[passportNumber], "Not found");
        return documents[passportNumber].qrCodeData;
    }
}
