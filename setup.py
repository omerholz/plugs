from setuptools import setup, find_packages
setup(
    name="sametrica.plugs",
    version="0.0.1",
    description='plug and compose callables together',
    url='https://github.com/Sametrica/plugs',
    zip_safe=False,
    packages=find_packages(),

    #metadata
    author="Omer Holzinger",
    author_email="omer@sametrica.com",
    organization="SAMETRICA",
    install_requires=[
    ],
    tests_require=[
        'sure==1.4.0','pytest==3.0.5'
    ]

)

