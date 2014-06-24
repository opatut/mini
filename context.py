import mini
from mini.models import Repository

repo = Repository()
repo.slug = "testrepo"

from mini.network import *

n = Network(repo)
n.generate()