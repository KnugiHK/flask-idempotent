from setuptools import setup

with open("README.rst") as d:
    __doc__ = d.read()

setup(
    name='Flask-Idempotent-Memory',
    version='0.1.1',
    url='https://github.com/KnugiHK/flask-idempotent-memory',
    license='MIT',
    author='Knugi (originally Flask-Idempotent by Franklyn Tackitt)',
    author_email='info@knugi.xyz',
    description='Idempotent requests for Flask applications using memory only',
    long_description=__doc__,
    py_modules=['flask_idempotent'],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'Flask>=0.9'
    ],
    long_description_content_type='text/markdown',
    keywords=['flask', 'api', "memory", "idempotent"],
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
