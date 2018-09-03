const blockchain = require('./blockchain');
const vote = new blockchain();

const bc1 =
{
"chain": [
{
"index": 1,
"timestamp": 1535988574646,
"transactions": [],
"nonce": 100,
"hash": "0",
"previousBlockHash": "0"
},
{
"index": 2,
"timestamp": 1535988582215,
"transactions": [],
"nonce": 16441,
"hash": "00009b2ef664890dbcd795344f8145bac1710db47cea457183f41c9ca24c3285",
"previousBlockHash": "0"
},
{
"index": 3,
"timestamp": 1535988587234,
"transactions": [
{
"amount": 12.5,
"sender": "00",
"recipient": "29366e50af8e11e8bbc735a3d8844e04",
"transactionId": "2dbe1950af8e11e8bbc735a3d8844e04"
}
],
"nonce": 63733,
"hash": "00005f4e73f8bc45ad24c1fbb48cd9ae61aee8ef35a39e76b0c46717d7de14bb",
"previousBlockHash": "00009b2ef664890dbcd795344f8145bac1710db47cea457183f41c9ca24c3285"
}
],
"pendingTransactions": [
{
"amount": 12.5,
"sender": "00",
"recipient": "29366e50af8e11e8bbc735a3d8844e04",
"transactionId": "30b7d150af8e11e8bbc735a3d8844e04"
}
],
"currentNodeUrl": "http://localhost:3001",
"networkNodes": []
};

console.log('VALID: ',vote.chainIsValid(bc1.chain));