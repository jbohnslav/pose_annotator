import setuptools

with open("README.md", 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='pose_annotator',
    version='0.0.1.post0',
    author='Jim Bohnslav',
    author_email='jbohnslav@gmail.com',
    description='Keypoint annotation GUI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
    entry_points={
        'console_scripts':[
            'pose_annotator = pose_annotator.gui.main:run']
    },
    python_requires='>=3.6',
    install_requires=['matplotlib',
                      'numpy',
                      'omegaconf>=2.0',
                      'opencv-python-headless',
                      'pandas',
                      'PySide2>=5.15',
                      'vidio>=0.0.3'], 
    url='https://github.com/jbohnslav/pose_annotator'
)
