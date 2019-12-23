import setuptools


setuptools.setup(
    name='contact-roster',
    packages=setuptools.find_packages(),
    install_requires=[
        "gunicorn",
        "django~=2.2.2",
        "mysqlclient<1.4",
        "django-guardian",
        "phpserialize",
        "bcrypt",
    ]
)
