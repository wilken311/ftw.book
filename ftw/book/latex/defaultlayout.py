from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.book import _
from ftw.book.interfaces import IBook
from ftw.book.interfaces import IBookLayoutBehavior
from ftw.book.latex.utils import get_raw_image_data
from ftw.pdfgenerator.babel import get_preferred_babel_option_for_context
from ftw.pdfgenerator.interfaces import IBuilder
from ftw.pdfgenerator.layout.makolayout import MakoLayoutBase
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.supermodel.model import Schema
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.i18n import translate
from zope.interface import Interface
from zope.interface import provider
from zope.schema import Int
from zope.schema import Text
from zope.schema import TextLine


@provider(IFormFieldProvider, IBookLayoutBehavior)
class IDefaultBookLayout(Schema):
    """Book instance behavior for a standard book layout.
    """

    release = TextLine(
        title=_(u'book_label_release', default=u'Release'),
        required=False,
        default=u'')

    book_author = TextLine(
        title=_(u'book_label_author', default=u'Author'),
        required=False,
        default=u'')

    author_address = Text(
        title=_(u'book_label_author_address', default=u'Author Address'),
        required=False,
        default=u'')

    titlepage_logo = NamedBlobImage(
        title=_(u'book_label_titlepage_logo', default=u'Titlepage logo'),
        description=_(u'book_help_titlepage_logo',
                      default=u'Upload an image or a PDF, which '
                      u'will be displayed on the titlepage'),
        required=False)

    titlepage_logo_width = Int(
        title=_(u'book_label_titlepage_logo_width',
                default=u'Titlepage logo width (%)'),
        description=_(u'book_help_titlepage_logo_width',
                      default=u'Width of the titlepage logo in '
                      u'percent of the content width.'),
        max=3,
        required=False,
        default=0)


@adapter(IDefaultBookLayout, Interface, IBuilder)
class DefaultBookLayout(MakoLayoutBase):

    template_directories = ['default_layout_templates']
    template_name = 'main.tex'

    def get_render_arguments(self):
        book = self.get_book()

        convert = self.get_converter().convert

        address = book.Schema().getField('author_address').get(book)
        address = convert(address.replace('\n', '<br />')).replace('\n', '')

        logo = book.Schema().getField('titlepage_logo').get(book)
        if logo and logo.data:
            logo_filename = 'titlepage_logo.jpg'
            self.get_builder().add_file(
                logo_filename,
                data=get_raw_image_data(logo.data))

            logo_width = book.Schema().getField(
                'titlepage_logo_width').get(book)
        else:
            logo_filename = False
            logo_width = 0

        args = {
            'context_is_book': self.context == book,
            'title': book.Title(),
            'use_titlepage': book.getUse_titlepage(),
            'logo': logo_filename,
            'logo_width': logo_width,
            'use_toc': book.getUse_toc(),
            'use_lot': book.getUse_lot(),
            'use_loi': book.getUse_loi(),
            'use_index': book.getUse_index(),
            'release': convert(book.Schema().getField('release').get(book)),
            'author': convert(book.Schema().getField('author').get(book)),
            'authoraddress': address,
            'babel': get_preferred_babel_option_for_context(self.context),
            'index_title': self.get_index_title(),
            }
        return args

    def get_book(self):
        obj = self.context
        while obj and not IBook.providedBy(obj):
            obj = aq_parent(aq_inner(obj))
        return obj

    def before_render_hook(self):
        self.use_package('inputenc', options='utf8', append_options=False)
        self.use_package('fontenc', options='T1', append_options=False)
        self.use_package('babel')
        self.use_package('times')
        self.use_package('fncychap', 'Sonny', append_options=False)
        self.use_package('longtable')
        self.use_package('sphinx')

        self.add_raw_template_file('sphinx.sty')
        self.add_raw_template_file('fncychap.sty')
        self.add_raw_template_file('sphinxftw.cls')
        self.add_raw_template_file('sphinxhowto.cls')
        self.add_raw_template_file('sphinxmanual.cls')

        # The sphinx document class requires graphicx and hyperref, so we
        # need to remove those packages from the document, otherwise it
        # would clash.
        self.remove_package('graphicx')
        self.remove_package('hyperref')

    def get_index_title(self):
        context_language_method = getattr(self.context, 'getLanguage', None)
        if context_language_method:
            language_code = context_language_method()

        else:
            ltool = getToolByName(self.context, 'portal_languages')
            language_code = ltool.getPreferredLanguage()

        return translate(_(u'title_index', default=u'Index'),
                         target_language=language_code)
