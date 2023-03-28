from efforting.mvp4.presets.text_processing import *


from template_renderer import template_tokenizer
from template_renderer import file_resource_renderer, local_template

# l = local_template.from_path(template_tokenizer, 'data/html/index.html')
# print(l.render('H', 'B').text)

#print(frr.template.positional_fields)
#print(frr.template.named_fields)

#print(frr.preview().text)


#frr = file_resource_renderer('data/html/index.html')

# print(frr.render(
# 	'<title>Test Title</title>',
# 	'Here be body',
# 	body_args=" onload='start_application()'"
# ).text)



