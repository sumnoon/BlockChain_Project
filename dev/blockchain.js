const sha256 = require('sha256');
const currentNodeUrl = process.argv[3];
const uuid = require('uuid/v1');

class BlockChain {
	constructor () {
		this.chain = [];
		this.pendingTransactions = []; 
		this.currentNodeUrl = currentNodeUrl;
		this.networkNodes = [];
		this.createNewBlock(100, '0', '0');
	}
	createNewBlock (nonce, previousBlockHash, hash) {
	// body...
		const newBlock = {
			index: this.chain.length + 1,
			timestamp: Date.now(),
			transactions: this.pendingTransactions,
			nonce: nonce,
			hash: hash,
			previousBlockHash: previousBlockHash
		};

		this.pendingTransactions = [];
		this.chain.push(newBlock);

		return newBlock;

	}
	getLastBlock( ) {
		// body...
		return this.chain[this.chain.length - 1];
	}

	createNewTransaction(amount, sender, recipient) {
		// body...
		const newTransaction = {
			amount: amount, 
			sender: sender,
			recipient: recipient,
			transactionId: uuid().split('-').join('')
		};

		return newTransaction;
	}

	addTransactionToPendingTransaction(transactionObj) {
		this.pendingTransactions.push(transactionObj);
		return this.getLastBlock()['index'] + 1;
	}

	hashBlock(previousBlockHash, currentBLockData, nonce) {
		// body...
		const dataAsString = previousBlockHash + nonce.toString() + JSON.stringify(currentBLockData);
		const hash = sha256(dataAsString);
		return hash;
	}

	proofOfWork(previousBlockHash, currentBLockData) {
		// vote.hashBlock(prviousBLockHash, currentBlockData, nonce);
		// repeatedly hash block until it finds correct hash => '000O1ANDHUVVNDHFD'
		// uses current block data fo rthe hash, but also the previousBLockHash
		// continuously change nonce value until it finds the correct hash
		// returns to us the nonce vaule that creates the correct hash
		let nonce = 0;
		let hash = this.hashBlock(previousBlockHash, currentBLockData, nonce);
		while(hash.substring(0, 4) != '0000'){
			nonce++;
			hash = this.hashBlock(previousBlockHash, currentBLockData, nonce);
			//console.log(hash);
		}
		return nonce;
	}
	chainIsValid (vote) {
		let validChain = true;
		for (var i = 1; i < vote.length && validChain; i++ ) {
			const currentBlcok = vote[i];
			const prevBlock = vote[i - 1];
			const blockHash = this.hashBlock(prevBlock['hash'], { transactions: currentBlockData, nonce: nonce});
			if ( blockHash.substring(0,4) !== '0000')validChain = false;
			if ( currentBlcok['previousBlockHash'] !== prevBlock['hash']) validChain = false;
			if ( !validChain ) return validChain;
		}

		const genesisBLock = vote[0];
		const correctNonce = genesisBLock['nonce'] === 100;
		const correctPreviousBlockHash = genesisBLock['previousBlockHash'] === '0';
		const correctHash = genesisBLock['hash'] === '0';
		const correctTransactions = genesisBLock['transactions'].length === 0;

		if( !correctNonce || !correctPreviousBlockHash || !correctHash || !correctTransactions ) validChain = false;
		return validChain; 

	}
}


module.exports = BlockChain;