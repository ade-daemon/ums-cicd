from setuptools import setup, find_packages

setup(
    name='auth-service',
    version='1.0.0',
    author='Adedamola Fasakin',
    description='Authentication service for UMS',
    packages=find_packages(),
    include_package_data=True,
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points={
        'console_scripts': [
            'auth-service=app:app'
        ]
    },
)
