from efforting.mvp6.mnemonic_language.processing import mnemonic_expression_to_regex, mnemonic_to_prepared_pattern


#print(mnemonic_expression_to_regex.process_item('signature'))
#print(mnemonic_expression_to_regex.process_item('signature as thing'))


print(mnemonic_to_prepared_pattern.process_item('stuff: {signature}'))
print(mnemonic_to_prepared_pattern.process_item('stuff: {signature as thing}'))

print(mnemonic_to_prepared_pattern.process_item('setup[:]').pattern)



