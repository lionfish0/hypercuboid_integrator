from distutils.core import setup
setup(
  name = 'hypercuboid_integrator',
  packages = ['hypercuboid_integrator'],
  version = '1.01',
  description = 'Integrate over a cuboid made of smaller cuboids',
  author = 'Mike Smith',
  author_email = 'm.t.smith@sheffield.ac.uk',
  url = 'https://github.com/lionfish0/hypercuboid_integrator.git',
  download_url = 'https://github.com/lionfish0/hypercuboid_integrator.git',
  keywords = ['integrating','hypercubes'],
  classifiers = [],
  install_requires=['numpy'],
)
