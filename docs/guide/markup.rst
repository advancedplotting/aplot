.. _guide_latex:

Using Inline Text Markup
========================

Any text that appears on a plot, including titles, axis labels, colorbar labels,
and text placed with :ref:`vi_text`, can contain inline markup.  The Toolkit
uses a subset of the "LaTeX" markup widely used in science and engineering.

Inline markup occurs between ``$`` characters in your string:
    
=========================================================== ==
``This is some example text with an $\alpha$ character.``
This is some example text with an :math:`\alpha` character.
=========================================================== ==

To put a literal ``$`` symbol in your string, simply escape it:

=========================================================== ==
``Alphas ($\alpha$) are expensive: \$2 each!``
Alphas (:math:`\alpha`) are expensive: $2 each!
=========================================================== ==

Ordinary letters appearing in markup will be treated as the names of
mathematical variables, and will appear in italic font.  You can manually
specify the font using the following commands:

=================== =======================
``\mathrm{Roman}``  :math:`\mathrm{Roman}`
``\mathrm{Italic}`` :math:`\mathit{Italic}`
=================== =======================

For function names (like ``cos`` or ``sin``), there's a better way:
see :ref:`guide_latex_functions` below.

If a string contains formatting mistakes or illegal characters, it will not
be processed by the LaTeX system.  Instead, the raw contents of the string
will be displayed.

.. only:: html

    Example
    -------

    Download :download:`Text Markup.vi </examples/Text Markup.vi>`,
    or see :ref:`guide_examples` for a complete list of examples.
    
    .. image:: TextExample.png


Basic Math
----------

=================================== ===============================
Result                              Code
=================================== ===============================
:math:`a_i^j`                       ``a_i^j``
:math:`a_{sub}^{super}`             ``a_{sub}^{super}``
:math:`\sqrt{a}`                    ``\sqrt{a}``
:math:`\sqrt[5]{a}`                 ``\sqrt[5]{a}``
:math:`\frac{a}{b}`                 ``\frac{a}{b}``
:math:`a = b`                       ``a = b``
:math:`a < b`                       ``a < b``
:math:`a > b`                       ``a > b``
:math:`a \leq b`                    ``a \leq b``
:math:`a \geq b`                    ``a \geq b``
:math:`a \ll b`                     ``a \ll b``
:math:`a \gg b`                     ``a \gg b``
:math:`a \approx b`                 ``a \approx b``
:math:`a \neq b`                    ``a \neq b``
:math:`a \times b`                  ``a \times b``
:math:`a \pm b`                     ``a \pm b``
:math:`\langle a \rangle`           ``\langle a \rangle``
:math:`\{a\}`                       ``\{ a \}``
:math:`\vec{a}`                     ``\vec{a}``
:math:`\acute{a}`                   ``\acute{a}``
:math:`\bar{a}`                     ``\bar{a}``
:math:`\dot{a}`                     ``\dot{a}``
:math:`\ddot{a}`                    ``\ddot{a}``
:math:`\hat{a}`                     ``\hat{a}``
=================================== ===============================


Math Symbols
------------

Keep in mind that some symbols, notably ``\int``, ``\prod``, and ``\sum``, 
have "smart" subscript and superscript support.  For example, this code::

    \int_{0}^{\infty} A(x) dx = \sum_{i=0}^{\infty} B_i
    
produces this result:

.. math::

    \int_{0}^{\infty} A(x) dx = \sum_{i=0}^{\infty} B_i

======================= ==================
Symbol                  Code
======================= ==================
:math:`\int`            ``\int``
:math:`\iint`           ``\iint``
:math:`\iiint`          ``\iiint``
:math:`\oint`           ``\oint``
:math:`\sum`            ``\sum``
:math:`\prod`           ``\prod``
:math:`\infty`          ``\infty``
:math:`\nabla`          ``\nabla``
:math:`\partial`        ``\partial``
:math:`\star`           ``\star``
:math:`\circ`           ``\circ``
:math:`\sim`            ``\sim``
:math:`\odot`           ``\odot``
:math:`\oplus`          ``\ominus``
:math:`\otimes`         ``\otimes``
:math:`\parallel`       ``\parallel``
:math:`\perp`           ``\perp``
:math:`\leftarrow`      ``\leftarrow``
:math:`\rightarrow`     ``\rightarrow``
:math:`\uparrow`        ``\uparrow``
:math:`\downarrow`      ``\downarrow``
======================= ==================


.. _guide_latex_functions:

Function Names
--------------

Plain characters inside a markup block are treated as the names of mathematical
variables.  This is undesirable when e.g. the sine of x is desired; ``sin x``
is rendered as :math:`sin x`.  The correct approach is to use the explicit
function name, via ``\sin{x}``: :math:`\sin{x}`.

======================= ==================
Function                Code
======================= ==================
:math:`\sin{x}`         ``\sin{x}``
:math:`\cos{x}`         ``\cos{x}``
:math:`\tan{x}`         ``\tan{x}``
:math:`\arcsin{x}`      ``\arcsin{x}``
:math:`\arccos{x}`      ``\arccos{x}``
:math:`\arctan{x}`      ``\arctan{x}``
:math:`\exp{x}`         ``\exp{x}``
:math:`\ln{x}`          ``\ln{x}``
:math:`\log{x}`         ``\log{x}``
======================= ==================

Greek Characters
----------------

These can be used anywhere an ordinary letter is used.  

=================== ==================
Character           Code
=================== ==================
:math:`\alpha`      ``\alpha``
:math:`\beta`       ``\beta``
:math:`\chi`        ``\chi``
:math:`\delta`      ``\delta``
:math:`\epsilon`    ``\epsilon``
:math:`\eta`        ``\eta``
:math:`\gamma`      ``\gamma``
:math:`\iota`       ``\iota``
:math:`\kappa`      ``\kappa``
:math:`\lambda`     ``\lambda``
:math:`\mu`         ``\mu``
:math:`\nu`         ``\nu``
:math:`\omega`      ``\omega``
:math:`\phi`        ``\phi``
:math:`\pi`         ``\pi``
:math:`\psi`        ``\psi``
:math:`\rho`        ``\rho``
:math:`\sigma`      ``\sigma``
:math:`\tau`        ``\tau``
:math:`\theta`      ``\theta``
:math:`\upsilon`    ``\upsilon``
:math:`\xi`         ``\xi``
:math:`\zeta`       ``\zeta``
:math:`\Delta`      ``\Delta``
:math:`\Gamma`      ``\Gamma``
:math:`\Lambda`     ``\Lambda``
:math:`\Omega`      ``\Omega``
:math:`\Phi`        ``\Phi``
:math:`\Pi`         ``\Pi``
:math:`\Psi`        ``\Psi``
:math:`\Sigma`      ``\Sigma``
:math:`\Theta`      ``\Theta``
:math:`\Upsilon`    ``\Upsilon``
:math:`\Xi`         ``\Xi``
=================== ==================




