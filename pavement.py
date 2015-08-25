# Copyright (c) 2014-2015, Heliosphere Research LLC
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
    Build automation Paver file.

    Each Paver command here represents one step of the build process.
    
    Requires the following environment variables.  If spaces occur in these
    paths, the full path MUST be quoted.
    
    LABVIEW:        Full path to "LabVIEW.exe"
    PYINSTALLER:    Full path to "pyinstaller.py"
    HHC:            Full path to Windows Help "hhc.exe"
"""

from paver.easy import sh, pushd, task, no_help, needs
import os.path as op
import shutil
import os
import zipfile
import glob
import time

# --- Support functions -------------------------------------------------------

def reset_dir(p, unlink=False):
    """ Create a new, empty directory, wiping out any existing directory. 
    
    If *unlink*, remove the directory but skip recreating it.
    """

    p = op.abspath(p)
    
    if op.splitdrive(p)[1] == '\\':
        raise ValueError("Can't reset drive root")
        
    if op.exists(p):
        print "Removing {}".format(p)
        shutil.rmtree(p)

    if not unlink:
        check_dir(p)


def check_dir(p):
    """ Create a directory if it doesn't already exist. """

    p = op.abspath(p)
    
    if op.exists(p):
        if not op.isdir(p):
            raise ValueError('"{}" exists but is not a directory'.format(p))
        return
        
    parts = p.split("\\")
    
    p = "{}\\".format(parts[0])

    for part in parts[1:]:
        p = op.join(p, part)
        print p
        if not op.exists(p):
            os.mkdir(p)

    
def zipdir(path, zipname):
    """ Zip up the contents of a directory """
    zipf = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for file in files:
            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), path))
    zipf.close()


# --- Documentation -----------------------------------------------------------
                    

@task
@needs('examples')
def docs_html():
    """ Build HTML documentation and deploy in export directory """

    staging_path = 'export\\staging_docs_html'
    
    reset_dir(staging_path)
    os.rmdir(staging_path) # for shutil.copytree
    
    shutil.copytree('docs', staging_path)
    shutil.copytree('export\\final_examples\\unpacked', op.join(staging_path, 'examples'))
    shutil.copy('export\\final_examples\\Examples.zip', op.join(staging_path, 'examples'))
        
    with pushd(staging_path):
        sh('make clean')
        sh('make html')
        
    html_path = 'export\\final_docs_html'
    reset_dir(html_path)
    os.rmdir(html_path)  # shutil.copytree demands to create it.  WHY NOT.
    
    shutil.copytree(op.join(staging_path, '_build\\html'), html_path)

    
@task
@needs('examples')
def docs_chm():
    """ Build CHM documentation and deploy in export directory """

    staging_path = 'export\\staging_docs_chm'
    
    reset_dir(staging_path)
    os.rmdir(staging_path) # for shutil.copytree
    
    shutil.copytree('docs', staging_path)
    shutil.copytree('export\\final_examples\\unpacked', op.join(staging_path, 'examples'))
    shutil.copy('export\\final_examples\\Examples.zip', op.join(staging_path, 'examples'))
        
    # Disable in-page nav boxes
    shutil.copy(op.join(staging_path, '_templates\\_layout_chm.html'), op.join(staging_path, '_templates\\layout.html'))

    with pushd(staging_path):
        sh('make clean')
        sh('make htmlhelp')
        
    sh('%HHC% {}'.format(op.join(staging_path, '_build\\htmlhelp\\AdvancedPlottingToolkit.hhp')), ignore_error=True)
    
    reset_dir('export\\final_docs_chm')
    shutil.copy(op.join(staging_path, '_build\\htmlhelp\\AdvancedPlottingToolkit.chm'), 'export\\final_docs_chm')


# --- VIP installer building --------------------------------------------------

@task
def pyinstaller():
    """ Build Python.zip and deploy it to final_pyinstaller """
    
    reset_dir('export\\final_pyinstaller')
    reset_dir('python\\build')
    reset_dir('python\\dist')
    
    with pushd('python'):
        sh('pyinstaller run.py')
    
    zipdir('python\\dist\\run', 'export\\final_pyinstaller\\Python.zip')


@task
@needs('docs_chm')
@needs('pyinstaller')
@needs('examples')
def build():
    """ Build release VIP package (with Python and proper Config.vi settings).
    """
    
    # Will hold the old-LabVIEW-exported VIs
    reset_dir('export\\staging_vip', unlink=True)
    shutil.copytree('labview', 'export\\staging_vip')
    
    # Patch in Python.zip and Config.vi changes    
    patcher_vi = op.abspath('export\\staging_vip\\PatchForRelease.vi')
    zip_path = op.abspath('export\\final_pyinstaller\\Python.zip')
    cmd = '%LABVIEW% "{}" -- "{}"'.format(patcher_vi, zip_path)
    sh(cmd)
    
    # Patch in new documentation
    shutil.copy('export\\final_docs_chm\\AdvancedPlottingToolkit.chm', 'export\\staging_vip')

    # Patch in examples
    reset_dir('export\\staging_vip\\examples', unlink=True)
    shutil.copytree('export\\final_examples\\unpacked', 'export\\staging_vip\\examples')

    # User can now build/install/distribute the VIP file
    print "Build finished.  You may now launch VIPM to package the Toolkit."
    

# --- Examples deployment -----------------------------------------------------

@task
def examples():
    """ Populate final_examples with Example.zip and unpacked examples """
    
    to_remove = [   'Examples.lvproj', 'Examples.aliases', 'Examples.lvlps',
                    'StandaloneDemo.vi', 'ExportDemos.vi', 'Performance.vi',
                    'Icon.ico', 'IconInstall.ico', 'EndUserLicenseAgreement.rtf',
                    'About.vi', 'Error.vi', 'Splash.vi']
                    
    reset_dir('export\\final_examples')
    reset_dir('export\\final_examples\\unpacked', unlink=True)
    #os.unlink('export\\final_examples\\unpacked')
    shutil.copytree('examples', 'export\\final_examples\\unpacked')
    
    # Don't publically release project file, etc.
    with pushd('export\\final_examples\\unpacked'):
        for f in to_remove:
            os.unlink(f)
            
    # Zip file containing all examples
    zipdir('export\\final_examples\\unpacked', 'export\\final_examples\\Examples.zip')


# --- Automated testing -------------------------------------------------------

@task
def test():
    """ Run a test suite and evaluate the results with LabVIEW.
    """
    
    
    vi_path = op.abspath(op.join('tests', "RunAndExit.vi"))
    cmd = '%LABVIEW% "{}"'.format(vi_path)
    
    # Run the LabVIEW test suite
    sh(cmd)
    
    output_dir = op.abspath(op.join('tests', 'output'))
    ref_dir = op.abspath(op.join('tests', 'ref'))
    script_path = op.abspath('tests\\check.py')
    
    cmd = 'python {} "{}" "{}"'.format(script_path, output_dir, ref_dir)
    
    # Run the Python checker
    sh(cmd, ignore_error=True)
 

@task
def clean_bincache():
    """ Reset user's bincache (PyInstaller directory) """
    d = os.environ['LOCALAPPDATA']
    if len(d) < 4:
        raise ValueError(d)
    d = op.join(d, "Advanced Plotting Toolkit")
    shutil.rmtree(d, True)

