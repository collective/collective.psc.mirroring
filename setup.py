from setuptools import setup, find_packages
import os

version = '0.1.3'

setup(name='collective.psc.mirroring',
      version=version,
      description="Event-based mirroring tool",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='psc disutils mirroring',
      author='Tarek Ziade',
      author_email='tarek@ziade.org',
      url='http://svn.plone.org/svn/collective/collective.psc.mirroring',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.psc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
