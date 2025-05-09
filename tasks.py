import pathlib
import subprocess

from invoke import task
from Ldap3Library import __version__ as VERSION
from Ldap3Library import Ldap3Library

ROOT = pathlib.Path(__file__).parent.resolve().as_posix()

@task
def utest(context):
    """Run unit tests."""
    subprocess.run(['coverage',
                    'run',
                    '--source=./Ldap3Library', 
                    '-m', 
                    'pytest',
                    '-s',
                    '-ra',
                    '-W ignore::DeprecationWarning',
                    f"{ROOT}/test/utest"
    ], check=False)
@task
def atest(context):
    """Run acceptance tests."""
    cmd = ['coverage',
            'run',
            '--source=./Ldap3Library', 
            '-m', 
            'robot',
            "--loglevel=TRACE:DEBUG",
            f"{ROOT}/test/atest"
        ]
    subprocess.run(" ".join(cmd), check=False)

@task(utest, atest)
def tests(context):
    """Run all tests."""
    subprocess.run('coverage combine', shell=True, check=False)
    subprocess.run('coverage report', shell=True, check=False)
    subprocess.run('coverage html', shell=True, check=False)

@task
def libdoc(context):
    print(f"Generating libdoc for library version {VERSION}")
    target = f"{ROOT}/docs/ldap3library.html"
    cmd = [
        "python",
        "-m",
        "robot.libdoc",
        "-n Ldap3Library",
        f"-v {VERSION}",
        "Ldap3Library",
        target,
    ]
    subprocess.run(" ".join(cmd), shell=True, check=False)

@task
def readme(context):
    with open(f"{ROOT}/docs/README.md", "w", encoding="utf-8") as readme:
        doc_string = Ldap3Library.__doc__
        readme.write(str(doc_string))