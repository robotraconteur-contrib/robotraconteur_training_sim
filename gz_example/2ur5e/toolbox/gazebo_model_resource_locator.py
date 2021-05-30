import tesseract
import re
import traceback
import os
from tesseract.tesseract_scene_graph import SimpleResourceLocator, SimpleResourceLocatorFn
#resource locator class using GAZEBO_MODEL_PATH and model:// url
class GazeboModelResourceLocatorFn:
	def __init__(self):
		model_env_path = os.environ["GAZEBO_MODEL_PATH"]
		self.model_paths = model_env_path.split(os.pathsep)
		assert len(self.model_paths) != 0, "No GAZEBO_MODEL_PATH specified!"
		for p in self.model_paths:
			assert os.path.isdir(p), "GAZEBO_MODEL_PATH directory does not exist: %s" % p

	def __call__(self,url):
		try:
			url_match = re.match(r"^model:\/\/(\w+)\/(.+)$",url)
			if (url_match is None):
				assert False, "Invalid Gazebo model resource url %s" % url
			model_name = url_match.group(1)
			resource_path = os.path.normpath(url_match.group(2))

			for p in self.model_paths:

				fname = os.path.join(p, model_name, resource_path )
				if not os.path.isfile(fname):
					continue
				return fname

			assert False, "Could not find requested resource %s" % url
		except:
			traceback.print_exc()
			return ""

def GazeboModelResourceLocator():
	locator_fn = SimpleResourceLocatorFn(GazeboModelResourceLocatorFn())
	locator = SimpleResourceLocator(locator_fn)
	locator_fn.__disown__()
	return locator