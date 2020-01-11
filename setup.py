from distutils.core import setup
from Cython.Build import cythonize

setup(
    name="crafter",
    ext_modules = cythonize("crafter/*.pyx", compiler_directives={"language_level": "3"})
)
