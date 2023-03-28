

//Some requests will need to be synchronous to the user, such as fetching the contents to display
//In such a case we will check the pending-request-queue and make sure it is empty

const pending_request_queue = new Queue();	//Todo - create class

function request_data(query) {

	const settings = {
		method: 'POST',
	}

	const rq = fetch(query.url, settings);
	rq.then(
		(r) => {	//Fulfilled
			console.log(r);
			query.on_success(r.json());
		},

		(r) => {	//Rejected
			console.log(r);
			query.on_failure(r.json());
		}
	);


}