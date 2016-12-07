from ftw.book.contents2.textblock import IBookTextBlockSchema
from ftw.book.helpers import BookHelper
from ftw.contentpage.browser import textblock_view
from ftw.simplelayout.contenttypes.browser.textblock import TextBlockView
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BookTextBlockView(TextBlockView):
    template = ViewPageTemplateFile('templates/textblock.pt')
    teaser_url = None

    @property
    def block_title(self):
        if not IBookTextBlockSchema(self.context).show_title:
            return ''
        return BookHelper()(self.context)


class BookTextBlockViewOLD(textblock_view.TextBlockView):

    def get_dynamic_title(self):
        return BookHelper()(self.context)


class HTMLBlockView(BrowserView):

    def get_dynamic_title(self):
        return BookHelper()(self.context)


class BookChapterView(BrowserView):

    def get_dynamic_title(self):
        return BookHelper()(self.context, linked=True)
