#!/bin/bash
# PRAMAAN - Hyperledger Fabric SmartBFT Setup Script
# This script downloads the official fabric-samples and starts the test-network with BFT consensus (4 orderers).

set -e

echo "Downloading Fabric binaries and samples (v3.0.0)..."
curl -sSLO https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/install-fabric.sh && chmod +x install-fabric.sh
./install-fabric.sh d s b

cd fabric-samples/test-network

echo "Starting Fabric test-network with SmartBFT (BFT) consensus..."
# -bft enables the BFT ordering service (4 nodes: 3f+1)
./network.sh up createChannel -c pramaan-channel -bft

echo "Deploying provenance chaincode..."
# Assumes chaincode is placed in ../../fabric/chaincode/provenance
./network.sh deployCC -ccn provenance -ccp ../../fabric/chaincode/provenance -ccl go -c pramaan-channel

echo "Fabric network successfully started with SmartBFT."
echo "Connection profiles and crypto material are in fabric-samples/test-network/organizations/"
