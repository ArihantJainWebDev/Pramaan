package main

import (
	"encoding/json"
	"fmt"
	"log"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type SmartContract struct {
	contractapi.Contract
}

// LedgerEvent represents a generic event stored on the ledger
type LedgerEvent struct {
	EventID       string `json:"event_id"`
	EventType     string `json:"event_type"` // DECRYPT_REQUEST, KEY_RELEASE, DECRYPT_ATTESTATION
	DocumentID    string `json:"document_id"`
	RecipientID   string `json:"recipient_id"`
	Timestamp     int64  `json:"timestamp"`
	PayloadStr    string `json:"payload_str"` // JSON string of the detailed event
	FingerprintID string `json:"fingerprint_id,omitempty"` // For attestations
}

// CreateDecryptRequest records a new decryption request
func (s *SmartContract) CreateDecryptRequest(ctx contractapi.TransactionContextInterface, eventID string, documentID string, recipientID string, timestamp int64, payloadStr string) error {
	exists, err := s.EventExists(ctx, eventID)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("the event %s already exists", eventID)
	}

	event := LedgerEvent{
		EventID:     eventID,
		EventType:   "DECRYPT_REQUEST",
		DocumentID:  documentID,
		RecipientID: recipientID,
		Timestamp:   timestamp,
		PayloadStr:  payloadStr,
	}
	
	eventJSON, err := json.Marshal(event)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(eventID, eventJSON)
}

// CommitDecryptAttestation records the final watermarking attestation
func (s *SmartContract) CommitDecryptAttestation(ctx contractapi.TransactionContextInterface, eventID string, documentID string, recipientID string, fingerprintID string, timestamp int64, payloadStr string) error {
	exists, err := s.EventExists(ctx, eventID)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("the event %s already exists", eventID)
	}

	event := LedgerEvent{
		EventID:       eventID,
		EventType:     "DECRYPT_ATTESTATION",
		DocumentID:    documentID,
		RecipientID:   recipientID,
		FingerprintID: fingerprintID,
		Timestamp:     timestamp,
		PayloadStr:    payloadStr,
	}
	
	eventJSON, err := json.Marshal(event)
	if err != nil {
		return err
	}

	// Also create an index for fingerprint lookup
	indexName := "fingerprint~event"
	indexKey, err := ctx.GetStub().CreateCompositeKey(indexName, []string{fingerprintID, eventID})
	if err != nil {
		return err
	}
	
	value := []byte{0x00}
	err = ctx.GetStub().PutState(indexKey, value)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(eventID, eventJSON)
}

// GetEvent retrieves an event by its ID
func (s *SmartContract) GetEvent(ctx contractapi.TransactionContextInterface, eventID string) (*LedgerEvent, error) {
	eventJSON, err := ctx.GetStub().GetState(eventID)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if eventJSON == nil {
		return nil, fmt.Errorf("the event %s does not exist", eventID)
	}

	var event LedgerEvent
	err = json.Unmarshal(eventJSON, &event)
	if err != nil {
		return nil, err
	}

	return &event, nil
}

// GetEventByFingerprint retrieves the attestation event for a given fingerprint ID
func (s *SmartContract) GetEventByFingerprint(ctx contractapi.TransactionContextInterface, fingerprintID string) (*LedgerEvent, error) {
	indexName := "fingerprint~event"
	resultsIterator, err := ctx.GetStub().GetStateByPartialCompositeKey(indexName, []string{fingerprintID})
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	if !resultsIterator.HasNext() {
		return nil, fmt.Errorf("no event found for fingerprint %s", fingerprintID)
	}

	responseRange, err := resultsIterator.Next()
	if err != nil {
		return nil, err
	}

	_, compositeKeyParts, err := ctx.GetStub().SplitCompositeKey(responseRange.Key)
	if err != nil {
		return nil, err
	}

	if len(compositeKeyParts) > 1 {
		eventID := compositeKeyParts[1]
		return s.GetEvent(ctx, eventID)
	}

	return nil, fmt.Errorf("invalid index key")
}

func (s *SmartContract) EventExists(ctx contractapi.TransactionContextInterface, eventID string) (bool, error) {
	eventJSON, err := ctx.GetStub().GetState(eventID)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}
	return eventJSON != nil, nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(&SmartContract{})
	if err != nil {
		log.Panicf("Error creating provenance chaincode: %v", err)
	}

	if err := chaincode.Start(); err != nil {
		log.Panicf("Error starting provenance chaincode: %v", err)
	}
}
