// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DocumentStorage {

    address public admin;

    constructor() {
        admin = msg.sender; // The deployer becomes the admin
    }

    struct Document {
        string docHash;      // BLAKE3 hash (off-chain computed)
        string qrCodeData;   // QR code string or metadata
        uint256 timestamp;   // Upload time
    }

    mapping(string => Document) private documents;  // passportNumber => Document
    mapping(string => bool) private exists;         // Prevent duplicates

    event DocumentStored(
        string indexed passportNumber,
        string docHash,
        string qrCodeData,
        uint256 timestamp
    );

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can store documents");
        _;
    }

    /// @notice Admin uploads a document’s BLAKE3 hash and QR code
    /// @param passportNumber Unique key for the document (e.g., passport number)
    /// @param docHash BLAKE3 hash of the uploaded document
    /// @param qrCodeData QR string related to the document
    function storeDocument(
        string memory passportNumber,
        string memory docHash,
        string memory qrCodeData
    ) public onlyAdmin {
        require(!exists[passportNumber], "Document already stored");
        require(bytes(passportNumber).length > 0, "Passport number required");
        require(bytes(docHash).length > 0, "Document hash required");

        documents[passportNumber] = Document({
            docHash: docHash,
            qrCodeData: qrCodeData,
            timestamp: block.timestamp
        });

        exists[passportNumber] = true;

        emit DocumentStored(passportNumber, docHash, qrCodeData, block.timestamp);
    }
}
