import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
	name='pynovice',
	version='0.0.6',
	description='data mining for novice and expert',
	url='https://github.com/wqwangchn/novice',
	author='wqwangchn',
	author_email='wqwangchn@163.com',
	long_description=long_description,
	long_description_content_type="text/markdown",
	packages=setuptools.find_packages(),
	install_requires = ['wordninja>=2.0.0','bert4keras>=0.6.5'],
	classifiers=[
	"Programming Language :: Python :: 3",
	"License :: OSI Approved :: MIT License",
	"Operating System :: OS Independent",
	],
	zip_safe=False
)
