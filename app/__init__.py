"""Knife-edge diffraction loss service.

Single knife-edge obstacle diffraction kernel exposed over HTTP.
Modules are deliberately independent:

- ``geometry``  : link geometry, wavelength and clearance
- ``fresnel``   : Fresnel-Kirchhoff parameter v and first Fresnel zone radius
- ``loss``      : diffraction loss approximation J(v)
- ``evaluator`` : composition of the above into evaluation results
- ``batch``     : batch scheduling of many links with per-item isolation
- ``schemas``   : HTTP input/output validation models
- ``presets``   : preset example links
- ``main``      : FastAPI interface layer
"""

__version__ = "1.0.0"
