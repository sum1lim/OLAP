from setuptools import setup

__version__ = (1, 0, 0)

setup(
    name='OLAP',
    description='Online Analytical Processing Queries',
    version='.'.join(str(d) for d in __version__),
    author='Sangwon Lim',
    author_email='sangwonl@uvic.ca',
    packages=['OLAP'],
    package_data = {
        'OLAP': [
            'tests/data/input.csv'
        ]
    },
    include_package_data=True,
    scripts='''
        ./scripts/OLAP
    '''.split(),

)
