from setuptools import setup, find_packages

setup(
    name='user-service',
    version='1.0.0',
    author='Adedamola Fasakin',
    description='User management service for UMS',
    packages=find_packages(),
    include_package_data=True,
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points={
        'console_scripts': [
            'user-service=app:app'
        ]
    },
)
