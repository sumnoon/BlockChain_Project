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
	const newTransaction = req.body;
	const blockIndex = vote.addTransactionToPendingTransaction(newTransaction);
	res.json({ note: `Transaction will be added in block ${blockIndex}.` })
});

// create a new transaction
// broadcast the transaction to all other network
app.post('/transaction/broadcast', function(req, res) {
	const newTransaction = vote.createNewTransaction(req.body.amount, req.body.sender, req.body.recipient);
	vote.addTransactionToPendingTransaction(newTransaction);

	const requestPromises = []
	vote.networkNodes.forEach(networkNodeUrl => {
		const requestOptions = {
			uri: networkNodeUrl + '/transaction',
			method: 'POST',
			body: newTransaction,
			json: true
		};

		requestPromises.push(rp(requestOptions));
	})

	Promise.all(requestPromises)
	.then(data => {
		res.json({ note: 'Transaction created and broadcast successfully' });
	});
});

// mine a new block
app.get('/mine', function(req, res){
	const lastBlock = vote.getLastBlock();
	const previousBlockHash = lastBlock['hash'];
	const currentBlockData = {
		transaction: vote.pendingTransactions,
		index: lastBlock['index'] + 1
	};
	const nonce = vote.proofOfWork(previousBlockHash, currentBlockData );
	const blockHash = vote.hashBlock(previousBlockHash, currentBlockData, nonce);
	const newBlock = vote.createNewBlock(nonce, previousBlockHash, blockHash);
	
	const requestPromises = [];
	vote.networkNodes.forEach(networkNodeUrl => {
		const requestOptions = {
			uri: networkNodeUrl + '/receive-new-block',
			method: 'POST',
			body: { newBlock: newBlock },
			json: true
		};

		requestPromises.push(rp(requestOptions));
	});

	Promise.all(requestPromises)
	.then(data => {
		const requestOptions = {
			uri: vote.currentNodeUrl + '/transaction/broadcast',
			method: 'POST',
			body: {
				amount: 12.5,
				sender: "00",
				recipient: nodeAddress
			},
			json: true
		};

		return rp(requestOptions);
	})
	.then(data => {
		res.json({
			note: "New block mined & broadcast successfully",
			block: newBlock
		});
	});
});

// to recive new block

app.post('/receive-new-block', function(req, res) { 
	const newBlock = req.body.newBlock;
	const lastBlock = vote.getLastBlock();
	const correctHash = lastBlock.hash === newBlock.previousBlockHash;
	const correctIndex = lastBlock['index'] + 1 === newBlock['index'];

	if (correctHash && correctIndex) {
		vote.chain.push(newBlock);
		vote.pendingTransactions = [];
		res.json({
			note: 'New block received and accepted.',
			newBlock: newBlock
		});
	} else {
		res.json({
			note: 'New block rejected.',
			newBlock: newBlock
		});
	}

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