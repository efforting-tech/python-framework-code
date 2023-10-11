import sys
from .presets import main_processor


for filename in sys.argv[1:]:
	main_processor.process_path(filename)