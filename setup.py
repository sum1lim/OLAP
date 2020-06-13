from setuptools import setup

__version__ = (0, 0, 1)

setup(
    name='OLAP',
    description='Online Analytical Processing Queries',
    version='.'.join(str(d) for d in __version__),
    author='Sangwon Lim',
    author_email='sangwonl@uvic.ca',
    packages=['OLAP'],
    include_package_data=True,
    scripts='''
        ./scripts/OLAP
    '''.split(),

)