# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models
from odoo.tools.translate import _
import lxml.etree as ET
import re
from odoo.exceptions import UserError
import base64
import binascii

from logging import getLogger

_logger = getLogger(__name__)

try:
    from asn1crypto import cms
except (ImportError, IOError) as err:
    _logger.debug(err)


re_base64 = re.compile(
    br'^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$')


def is_base64(s):
    s = s or b""
    s = s.replace(b"\r", b"").replace(b"\n", b"")
    return re_base64.match(s)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def remove_xades_sign(self, xml):
        # Recovering parser is needed for files where strings like
        # xmlns:ds="http://www.w3.org/2000/09/xmldsig#&quot;"
        # are present: even if lxml raises
        # {XMLSyntaxError}xmlns:ds:
        # 'http://www.w3.org/2000/09/xmldsig#"' is not a valid URI
        # such files are accepted by SDI
        recovering_parser = ET.XMLParser(recover=True)
        root = ET.XML(xml, parser=recovering_parser)
        for elem in root.iter('*'):
            if elem.tag.find('Signature') > -1:
                elem.getparent().remove(elem)
                break
        return ET.tostring(root)

    def strip_xml_content(self, xml):
        recovering_parser = ET.XMLParser(recover=True)
        root = ET.XML(xml, parser=recovering_parser)
        return ET.tostring(root)

    @staticmethod
    def extract_cades(data):
        info = cms.ContentInfo.load(data)
        return info['content']['encap_content_info']['content'].native

    def cleanup_xml(self, xml_string):
        xml_string = self.remove_xades_sign(xml_string)
        xml_string = self.strip_xml_content(xml_string)
        return xml_string

    def get_xml_string(self):
        try:
            data = base64.b64decode(self.datas)
        except binascii.Error as e:
            raise UserError(
                _(
                    'Corrupted attachment %s.'
                ) % e.args
            )

        if is_base64(data):
            try:
                data = base64.b64decode(data)
            except binascii.Error as e:
                raise UserError(
                    _(
                        'Base64 encoded file %s.'
                    ) % e.args
                )

        # Amazon sends xml files without <?xml declaration,
        # so they cannot be easily detected using a pattern.
        # We first try to parse as asn1, if it fails we assume xml

        # asn1crypto parser will raise ValueError
        # if the asn1 cannot be parsed
        # KeyError is raised if one of the needed key is not
        # in the asn1 structure (info->content->encap_content_info->content)
        try:
            data = self.extract_cades(data)
        except (ValueError, KeyError):
            pass

        try:
            return self.cleanup_xml(data)
        # cleanup_xml calls root.iter(), but root is None if the parser fails
        # Invalid xml 'NoneType' object has no attribute 'iter'
        except AttributeError as e:
            raise UserError(
                _(
                    'Invalid xml %s.'
                ) % e.args
            )