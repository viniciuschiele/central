from setuptools import setup

setup(
    name='Central',
    version='0.6.0',
    packages=['central', 'central.config'],
    url='https://github.com/viniciuschiele/central',
    license='MIT',
    author='Vinicius Chiele',
    author_email='vinicius.chiele@gmail.com',
    description='A dynamic configuration library',
    keywords=['config', 'configuration', 'dynamic', 'file', 's3', 'aws', 'storage', 'reload'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
