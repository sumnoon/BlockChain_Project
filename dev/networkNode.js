const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const Blockchain = require('./blockchain');
const uuid = require('uuid/v1');
const port = process.argv[2];
const rp = require('request-promise'); // rp = request promise

const nodeAddress = uuid().split('-').join('');

const vote = new Blockchain();


app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

// get enitre blockchain
app.get('/blockchain', function(req, res){
	res.send(vote);
});

// create a new transaction
app.post('/transaction', function(req, res) {
	const voteIndex = vote.createNewTransaction(req.body.amount, req.body.sender, req.body.recipient);
	res.json({ note: `Transaction will be added in block ${voteIndex}.`});
});

app.get('/mine', function(req, res){
	const lastBlock = vote.getLastBlock();
	const previousBlockHash = lastBlock['hash'];
	const currentBlockData = {
		transaction: vote.pendingTransactions,
		index: lastBlock['index'] + 1
	};
	const nonce = vote.proofOfWork(previousBlockHash, currentBlockData );
	const blockHash = vote.hashBlock(previousBlockHash, currentBlockData, nonce);

	vote.createNewTransaction(12.5, "00", nodeAddress);

	const newBlock = vote.createNewBlock(nonce, previousBlockHash, blockHash);
	res.json({
		note: "New block mined successfully",
		block: newBlock
	});
});

// register a node and broadcast it to the entire network
app.post('/register-and-broadcast-node', function(req, res){
	const newNodeUrl = req.body.newNodeUrl;
	if (vote.networkNodes.indexOf(newNodeUrl) == -1)vote.networkNodes.push(newNodeUrl);
	//-----Broadcast

	const regNodesPromises = [];
	vote.networkNodes.forEach(networkNodesUrl => {
		const requestOptions = {
			uri: networkNodesUrl + '/register-node',
			method: 'POST',
			body: { newNodeUrl: newNodeUrl },
			json: true
		};
		
		regNodesPromises.push(rp(requestOptions));
	});

	Promise.all(regNodesPromises)
	.then(data => {
		const bulkRegisterOptions = {
			uri: newNodeUrl + '/register-nodes-bulk',
			method: 'POST',
			body: { allNetworkNodes: [ ...vote.networkNodes, vote.currentNodeUrl ] },
			json: true
		};

		return rp(bulkRegisterOptions);
		// use the data.....
	})
	.then(data => {
		res.json({ note: 'New node registered with network successfully' });
	});
});

// register a node with the network
app.post('/register-node', function(req, res){
	const newNodeUrl = req.body.newNodeUrl;
	const nodeNotAlreadyPresent = vote.networkNodes.indexOf(newNodeUrl) == -1;
	const notCurrentNode = vote.currentNodeUrl !== newNodeUrl;
	if (nodeNotAlreadyPresent && notCurrentNode) vote.networkNodes.push(newNodeUrl);
	res.json({ note: 'New node registered successful.' });
});


// register multiple nodes at once
app.post('/register-nodes-bulk', function(req, res){
	const allNetworkNodes = req.body.allNetworkNodes;
	allNetworkNodes.forEach(networkNodeUrl => {
		const nodeNotAlreadyPresent = vote.networkNodes.indexOf(networkNodeUrl) == -1;
		const notCurrentNode = vote.currentNodeUrl !== networkNodeUrl;
		if (nodeNotAlreadyPresent && notCurrentNode) vote.networkNodes.push(networkNodeUrl);
	});

	res.json({ note: 'Bulk registration successful.' });
});


app.listen(port, function(){
	console.log(`Listening on port ${port}...`);
});