const express = require('express');
const { connect, signers } = require('@hyperledger/fabric-gateway');
const fs = require('fs');
const path = require('path');
const grpc = require('@grpc/grpc-js');

const app = express();
app.use(express.json());

const channelName = 'pramaan-channel';
const chaincodeName = 'provenance';

// Helper function to create gRPC connection
async function newGrpcConnection() {
    const tlsCertPath = path.resolve(__dirname, '../fabric/network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt');
    const tlsRootCert = fs.readFileSync(tlsCertPath);
    const tlsCredentials = grpc.credentials.createSsl(tlsRootCert);
    return new grpc.Client('localhost:7051', tlsCredentials, {
        'grpc.ssl_target_name_override': 'peer0.org1.example.com',
    });
}

// Helper to get Gateway connection
async function getGateway(client) {
    const certPath = path.resolve(__dirname, '../fabric/network/organizations/peerOrganizations/org1.example.com/users/User1@org1.example.com/msp/signcerts/cert.pem');
    const keyDir = path.resolve(__dirname, '../fabric/network/organizations/peerOrganizations/org1.example.com/users/User1@org1.example.com/msp/keystore');
    const keyFiles = fs.readdirSync(keyDir);
    const keyPath = path.join(keyDir, keyFiles[0]);

    const certificate = fs.readFileSync(certPath);
    const privateKey = fs.readFileSync(keyPath);

    const identity = { mspId: 'Org1MSP', credentials: certificate };
    const signer = signers.newPrivateKeySigner(privateKey);

    return connect({
        client,
        identity,
        signer,
    });
}

app.post('/transactions/:functionName', async (req, res) => {
    let client, gateway;
    try {
        client = await newGrpcConnection();
        gateway = await getGateway(client);
        
        const network = gateway.getNetwork(channelName);
        const contract = network.getContract(chaincodeName);
        
        const args = Object.values(req.body);
        
        await contract.submitTransaction(req.params.functionName, ...args);
        res.status(200).send({ status: 'success' });
    } catch (err) {
        console.error(err);
        res.status(500).send({ error: err.message });
    } finally {
        if (gateway) gateway.close();
        if (client) client.close();
    }
});

app.get('/queries/:functionName/:arg', async (req, res) => {
    let client, gateway;
    try {
        client = await newGrpcConnection();
        gateway = await getGateway(client);
        
        const network = gateway.getNetwork(channelName);
        const contract = network.getContract(chaincodeName);
        
        const resultBytes = await contract.evaluateTransaction(req.params.functionName, req.params.arg);
        const resultJson = new TextDecoder().decode(resultBytes);
        res.status(200).send(JSON.parse(resultJson));
    } catch (err) {
        if (err.message.includes('no event found')) {
            res.status(404).send({ error: 'Not found' });
        } else {
            console.error(err);
            res.status(500).send({ error: err.message });
        }
    } finally {
        if (gateway) gateway.close();
        if (client) client.close();
    }
});

app.listen(3000, () => {
    console.log('Fabric Gateway Adapter running on port 3000');
});
