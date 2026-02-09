Advanced Plotting Toolkit
=========================

This is the project source code for the Advanced Plotting Toolkit, an add-on
which brings modern visualization to the LabVIEW platform by wrapping
matplotlib.

Originally a commercial project, the Toolkit is now open-source!
If you are interested in participating, get in touch on the forum at NI.com:

https://decibel.ni.com/content/groups/advanced-plotting-toolkit

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

Download & Install
==================

The Toolkit is currently distributed through the LabVIEW Tools Network.  You
can install it through VIPM (2014 or later).  Read the Tools Network page here:

http://sine.ni.com/nips/cds/view/p/lang/en/nid/213166

Installable artifacts may also be available on GitHub:

https://github.com/advancedplotting/aplot/releases

Developing
==========

Here are some basic build instructions to get you started hacking on the
Toolkit.  The Toolkit can be built with LabVIEW 2013 or later, and VIPM 2014
free edition.

Please be aware that because the Toolkit was originally developed as a
commercial product targeting LabVIEW versions as old as 2013-2015, the
toolchain is somewhat behind the modern state of the art.  Requirements
needed for building the toolkit itself are pinned in
environment/requirements.txt, but some experimentation may be required to get
the build tools themselves (e.g. paver) in good working order.

**Pull requests are welcome for more recent platforms (e.g. Windows 11).**

Important notes
---------------

* Windows 7 64-bit required (Windows 10 and 11 are likely to work but less tested)
* Don't open the .vip file until you have run at least one build through paver.
  You will lose the palettes and have to recreate them.  See "Build Procedure"
  below.

Set up toolchain
----------------

* Install Git
* Use Git to clone the source tree into ``C:\aplot``
    * Yes, it *must* be ``C:\aplot`` or things won't work.  This limitation
      comes from the interface between the build automation and the VIPM
      packaging machinery; a pre-arranged (hardcoded) path is needed.
* Install LabVIEW 2013 SP1 or later
* Install VIPM 2014 or later
* (Optional) Install Microsoft HTML Help Workshop 1.3.  This is needed for
  embedded context help in older LabVIEW versions.
* Install Python 2.7 from Python.org, into ``C:\Python27``
    - Ensure that Python.exe and pip.exe are on your path.  This is an option
      in the installer.
* Install core Python packages NumPy, Matplotlib, and PyWin32
    - These are available in the "requirements" directory of the source tree
* Install additional Python packages, using pip:
    - pip install wheel
    - pip install sphinx
    - pip install pyinstaller
    - pip install psutil
    - pip install python-dateutil
    - pip install pyparsing
    - pip install pillow
    - pip install paver
  
Set up build environment
------------------------
 
Create the following environment variables:
 
* %LABVIEW%: Full path to LabVIEW.exe
* %PYINSTALLER%: Full path to pyinstaller.exe, somewhere in ``C:\Python27``
* %HHC%: Full path to Windows HTML Help Workshop hhc.exe
 
Build procedure
---------------
 
Open a command prompt and navigate to ``C:\aplot``.  Output files will emerge
in ``C:\aplot\export``.  Shut down LabVIEW before proceeding.

1. Run "paver build".  This sets everything up for packaging with VIPM.
2. Double-click the .vipb file, and build the project in VIPM
3. [Optional] Install the new VIP file through VIPM
4. [Optional] Run "paver test" to run the test suite

Other stand-alone commands:

* Run "paver docs_html" to build just the HTML documentation
* Run "paver docs_chm" to build just the CHM documentation

    
