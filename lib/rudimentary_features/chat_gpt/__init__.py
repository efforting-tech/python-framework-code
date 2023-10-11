import openai

#TODO - maybe not a "global" openai api_key

def load_openai_secret(path):
	openai.api_key = path.read_text().strip()

#Base chatbot class
class chatbot_base:
	recount_history = 3
	model = 'gpt-3.5-turbo'
	initial_system_messages = (
		'You are a helpful, cheerful and generally excited creative assistant',
	)

	def __init__(self, model=None, initial_system_messages=None, recount_history=None):
		if initial_system_messages is not None:
			self.initial_system_messages = initial_system_messages

		if model is not None:
			self.model = model

		if recount_history is not None:
			self.recount_history = recount_history

		self.history = list()

	def get_messages(self, recount_history=None):
		if recount_history is None:
			recount_history = self.recount_history
		result = list(dict(role='system', content=sm) for sm in self.initial_system_messages)

		for m in self.history[-recount_history:]:
			if m['role'] == 'query':
				result.append(m['query'])
				result.append(m['answer'])
			elif m['role'] == 'user':
				result.append(m)

		return result



class synchronous_chatbot(chatbot_base):
	def external_query(self, messages):
		result = openai.ChatCompletion.create(
			model=self.model,
			messages=messages,
		)

		[c] = result.choices    #Expect a single response
		return c['message']

	def query(self, prompt):
		pending_message = dict(role='user', content=prompt)
		messages = self.get_messages()
		messages.append(pending_message)
		answer = self.external_query(messages)
		self.history.append(dict(role='query', query=pending_message, answer=answer))
		return answer['content'].strip()

#There was no asynchronous implementation, chatgpt just made that up!!


# class asynchronous_chatbot(chatbot_base):
# 	async def query(self, prompt):
# 		pending_message = dict(role='user', content=prompt)
# 		messages = self.get_messages()
# 		messages.append(pending_message)
# 		answer = await self.external_query(messages)
# 		self.history.append(dict(role='query', query=pending_message, answer=answer))
# 		return answer['content'].strip()

# 	async def external_query(self, messages):
# 		result = await openai.ChatCompletion.create_async(
# 			model=self.model,
# 			messages=messages,
# 		)

# 		[c] = result.choices    #Expect a single response
# 		return c['message']
